"""
Phase 3 ML Training Service
Training XGBoost, LightGBM, and LSTM models for trading signals
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import joblib
import pickle
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from django.utils import timezone
from django.db import transaction

from apps.signals.models import MLModel, MLTrainingSession, MLFeature, MLModelPerformance
from apps.signals.ml_data_service import MLDataCollectionService
from apps.trading.models import Symbol

logger = logging.getLogger(__name__)


class MLTrainingService:
    """Service for training ML models for trading signals"""
    
    def __init__(self):
        self.logger = logger
        self.data_service = MLDataCollectionService()
        self.models_dir = "ml_models/"
        
    def train_xgboost_model(self, symbols: List[Symbol], model_name: str, 
                          target_variable: str = 'signal_direction',
                          prediction_horizon_hours: int = 24,
                          training_days: int = 365) -> MLModel:
        """
        Train XGBoost model for classification/regression
        
        Args:
            symbols: List of symbols to train on
            model_name: Name for the model
            target_variable: Target variable to predict
            prediction_horizon_hours: Hours ahead to predict
            training_days: Days of training data
            
        Returns:
            Trained MLModel instance
        """
        try:
            self.logger.info(f"Training XGBoost model: {model_name}")
            
            # Create model record
            end_date = timezone.now()
            start_date = end_date - timedelta(days=training_days)
            
            model = MLModel.objects.create(
                name=model_name,
                model_type='XGBOOST',
                target_variable=target_variable,
                prediction_horizon=prediction_horizon_hours,
                training_start_date=start_date,
                training_end_date=end_date,
                validation_start_date=start_date + timedelta(days=training_days * 0.8),
                validation_end_date=end_date,
                status='TRAINING'
            )
            
            # Create training session
            session = MLTrainingSession.objects.create(
                model=model,
                session_name=f"{model_name}_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                status='STARTED'
            )
            
            try:
                # Collect training data
                session.status = 'DATA_PREPARATION'
                session.current_step = 'Collecting training data'
                session.save()
                
                training_data = self.data_service.collect_training_data(
                    symbols, start_date, end_date, prediction_horizon_hours
                )
                
                if training_data.empty:
                    raise ValueError("No training data collected")
                
                # Prepare features and labels
                session.status = 'FEATURE_ENGINEERING'
                session.current_step = 'Engineering features'
                session.save()
                
                X, y, feature_names = self._prepare_features_labels(training_data, target_variable)
                
                # Split data
                X_train, X_val, y_train, y_val = self._split_data(X, y)
                
                # Train model
                session.status = 'TRAINING'
                session.current_step = 'Training XGBoost model'
                session.save()
                
                xgb_model, scaler = self._train_xgboost(X_train, y_train, X_val, y_val, target_variable)
                
                # Evaluate model
                session.status = 'VALIDATION'
                session.current_step = 'Validating model'
                session.save()
                
                metrics = self._evaluate_model(xgb_model, X_val, y_val, target_variable)
                
                # Save model
                model_path = self._save_model(xgb_model, scaler, model_name)
                
                # Update model record
                model.model_file_path = model_path
                model.scaler_file_path = model_path.replace('.pkl', '_scaler.pkl')
                model.features_used = feature_names
                model.status = 'TRAINED'
                model.training_samples = len(X_train)
                model.validation_samples = len(X_val)
                
                # Update metrics
                for metric_name, metric_value in metrics.items():
                    setattr(model, metric_name, metric_value)
                
                model.save()
                
                # Update session
                session.status = 'COMPLETED'
                session.completed_at = timezone.now()
                session.duration_seconds = (session.completed_at - session.started_at).total_seconds()
                session.training_metrics = metrics
                session.save()
                
                self.logger.info(f"XGBoost model {model_name} trained successfully")
                return model
                
            except Exception as e:
                # Handle training failure
                model.status = 'FAILED'
                model.save()
                
                session.status = 'FAILED'
                session.error_message = str(e)
                session.completed_at = timezone.now()
                session.save()
                
                raise e
                
        except Exception as e:
            self.logger.error(f"Error training XGBoost model: {e}")
            raise e
    
    def train_lightgbm_model(self, symbols: List[Symbol], model_name: str,
                           target_variable: str = 'signal_direction',
                           prediction_horizon_hours: int = 24,
                           training_days: int = 365) -> MLModel:
        """Train LightGBM model"""
        try:
            self.logger.info(f"Training LightGBM model: {model_name}")
            
            # Similar structure to XGBoost training
            end_date = timezone.now()
            start_date = end_date - timedelta(days=training_days)
            
            model = MLModel.objects.create(
                name=model_name,
                model_type='LIGHTGBM',
                target_variable=target_variable,
                prediction_horizon=prediction_horizon_hours,
                training_start_date=start_date,
                training_end_date=end_date,
                validation_start_date=start_date + timedelta(days=training_days * 0.8),
                validation_end_date=end_date,
                status='TRAINING'
            )
            
            session = MLTrainingSession.objects.create(
                model=model,
                session_name=f"{model_name}_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                status='STARTED'
            )
            
            try:
                # Collect and prepare data
                training_data = self.data_service.collect_training_data(
                    symbols, start_date, end_date, prediction_horizon_hours
                )
                
                X, y, feature_names = self._prepare_features_labels(training_data, target_variable)
                X_train, X_val, y_train, y_val = self._split_data(X, y)
                
                # Train LightGBM
                lgb_model, scaler = self._train_lightgbm(X_train, y_train, X_val, y_val, target_variable)
                
                # Evaluate and save
                metrics = self._evaluate_model(lgb_model, X_val, y_val, target_variable)
                model_path = self._save_model(lgb_model, scaler, model_name)
                
                # Update model
                model.model_file_path = model_path
                model.scaler_file_path = model_path.replace('.pkl', '_scaler.pkl')
                model.features_used = feature_names
                model.status = 'TRAINED'
                model.training_samples = len(X_train)
                model.validation_samples = len(X_val)
                
                for metric_name, metric_value in metrics.items():
                    setattr(model, metric_name, metric_value)
                
                model.save()
                
                session.status = 'COMPLETED'
                session.completed_at = timezone.now()
                session.training_metrics = metrics
                session.save()
                
                self.logger.info(f"LightGBM model {model_name} trained successfully")
                return model
                
            except Exception as e:
                model.status = 'FAILED'
                model.save()
                session.status = 'FAILED'
                session.error_message = str(e)
                session.save()
                raise e
                
        except Exception as e:
            self.logger.error(f"Error training LightGBM model: {e}")
            raise e
    
    def train_lstm_model(self, symbols: List[Symbol], model_name: str,
                        target_variable: str = 'signal_direction',
                        prediction_horizon_hours: int = 24,
                        training_days: int = 365,
                        sequence_length: int = 60) -> MLModel:
        """Train LSTM model for sequential data"""
        try:
            self.logger.info(f"Training LSTM model: {model_name}")
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=training_days)
            
            model = MLModel.objects.create(
                name=model_name,
                model_type='LSTM',
                target_variable=target_variable,
                prediction_horizon=prediction_horizon_hours,
                training_start_date=start_date,
                training_end_date=end_date,
                validation_start_date=start_date + timedelta(days=training_days * 0.8),
                validation_end_date=end_date,
                status='TRAINING'
            )
            
            session = MLTrainingSession.objects.create(
                model=model,
                session_name=f"{model_name}_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                status='STARTED'
            )
            
            try:
                # Collect training data
                training_data = self.data_service.collect_training_data(
                    symbols, start_date, end_date, prediction_horizon_hours
                )
                
                # Prepare sequential data
                X, y, feature_names = self._prepare_sequential_data(training_data, target_variable, sequence_length)
                X_train, X_val, y_train, y_val = self._split_data(X, y)
                
                # Train LSTM
                lstm_model, scaler = self._train_lstm(X_train, y_train, X_val, y_val, target_variable)
                
                # Evaluate and save
                metrics = self._evaluate_model(lstm_model, X_val, y_val, target_variable)
                model_path = self._save_model(lstm_model, scaler, model_name)
                
                # Update model
                model.model_file_path = model_path
                model.scaler_file_path = model_path.replace('.pkl', '_scaler.pkl')
                model.features_used = feature_names
                model.status = 'TRAINED'
                model.training_samples = len(X_train)
                model.validation_samples = len(X_val)
                
                for metric_name, metric_value in metrics.items():
                    setattr(model, metric_name, metric_value)
                
                model.save()
                
                session.status = 'COMPLETED'
                session.completed_at = timezone.now()
                session.training_metrics = metrics
                session.save()
                
                self.logger.info(f"LSTM model {model_name} trained successfully")
                return model
                
            except Exception as e:
                model.status = 'FAILED'
                model.save()
                session.status = 'FAILED'
                session.error_message = str(e)
                session.save()
                raise e
                
        except Exception as e:
            self.logger.error(f"Error training LSTM model: {e}")
            raise e
    
    def _prepare_features_labels(self, data: pd.DataFrame, target_variable: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and labels for training"""
        try:
            # Select feature columns (exclude target and metadata)
            exclude_columns = [
                'symbol', 'symbol_id', 'timestamp', 'future_price', 'future_return',
                'signal_direction', 'is_profitable', 'target_return', 'target_volatility'
            ]
            
            feature_columns = [col for col in data.columns if col not in exclude_columns]
            X = data[feature_columns].values
            
            # Handle target variable
            if target_variable in data.columns:
                y = data[target_variable].values
            else:
                raise ValueError(f"Target variable {target_variable} not found in data")
            
            # Remove NaN values
            valid_indices = ~(np.isnan(X).any(axis=1) | np.isnan(y))
            X = X[valid_indices]
            y = y[valid_indices]
            
            return X, y, feature_columns
            
        except Exception as e:
            self.logger.error(f"Error preparing features and labels: {e}")
            raise e
    
    def _prepare_sequential_data(self, data: pd.DataFrame, target_variable: str, sequence_length: int) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare sequential data for LSTM training"""
        try:
            # Sort by timestamp
            data = data.sort_index()
            
            # Select feature columns
            exclude_columns = [
                'symbol', 'symbol_id', 'timestamp', 'future_price', 'future_return',
                'signal_direction', 'is_profitable', 'target_return', 'target_volatility'
            ]
            
            feature_columns = [col for col in data.columns if col not in exclude_columns]
            feature_data = data[feature_columns].values
            
            # Create sequences
            X_sequences = []
            y_sequences = []
            
            for i in range(sequence_length, len(feature_data)):
                X_sequences.append(feature_data[i-sequence_length:i])
                y_sequences.append(data[target_variable].iloc[i])
            
            X = np.array(X_sequences)
            y = np.array(y_sequences)
            
            # Remove NaN values
            valid_indices = ~(np.isnan(X).any(axis=(1, 2)) | np.isnan(y))
            X = X[valid_indices]
            y = y[valid_indices]
            
            return X, y, feature_columns
            
        except Exception as e:
            self.logger.error(f"Error preparing sequential data: {e}")
            raise e
    
    def _split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into train and validation sets"""
        try:
            # Use time series split for temporal data
            split_idx = int(len(X) * (1 - test_size))
            
            X_train = X[:split_idx]
            X_val = X[split_idx:]
            y_train = y[:split_idx]
            y_val = y[split_idx:]
            
            return X_train, X_val, y_train, y_val
            
        except Exception as e:
            self.logger.error(f"Error splitting data: {e}")
            raise e
    
    def _train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray, 
                      X_val: np.ndarray, y_val: np.ndarray, target_variable: str) -> Tuple[Any, StandardScaler]:
        """Train XGBoost model"""
        try:
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Determine objective
            if target_variable in ['signal_direction', 'is_profitable']:
                objective = 'multi:softmax' if len(np.unique(y_train)) > 2 else 'binary:logistic'
                num_class = len(np.unique(y_train)) if len(np.unique(y_train)) > 2 else None
            else:
                objective = 'reg:squarederror'
                num_class = None
            
            # Train model
            params = {
                'objective': objective,
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }
            
            if num_class:
                params['num_class'] = num_class
            
            model = xgb.XGBClassifier(**params) if objective != 'reg:squarederror' else xgb.XGBRegressor(**params)
            model.fit(X_train_scaled, y_train, 
                     eval_set=[(X_val_scaled, y_val)],
                     early_stopping_rounds=10,
                     verbose=False)
            
            return model, scaler
            
        except Exception as e:
            self.logger.error(f"Error training XGBoost: {e}")
            raise e
    
    def _train_lightgbm(self, X_train: np.ndarray, y_train: np.ndarray,
                       X_val: np.ndarray, y_val: np.ndarray, target_variable: str) -> Tuple[Any, StandardScaler]:
        """Train LightGBM model"""
        try:
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Determine objective
            if target_variable in ['signal_direction', 'is_profitable']:
                objective = 'multiclass' if len(np.unique(y_train)) > 2 else 'binary'
                num_class = len(np.unique(y_train)) if len(np.unique(y_train)) > 2 else None
            else:
                objective = 'regression'
                num_class = None
            
            # Train model
            params = {
                'objective': objective,
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'verbose': -1
            }
            
            if num_class:
                params['num_class'] = num_class
            
            model = lgb.LGBMClassifier(**params) if objective != 'regression' else lgb.LGBMRegressor(**params)
            model.fit(X_train_scaled, y_train,
                     eval_set=[(X_val_scaled, y_val)],
                     callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)])
            
            return model, scaler
            
        except Exception as e:
            self.logger.error(f"Error training LightGBM: {e}")
            raise e
    
    def _train_lstm(self, X_train: np.ndarray, y_train: np.ndarray,
                   X_val: np.ndarray, y_val: np.ndarray, target_variable: str) -> Tuple[Any, StandardScaler]:
        """Train LSTM model"""
        try:
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
            X_val_scaled = scaler.transform(X_val.reshape(-1, X_val.shape[-1])).reshape(X_val.shape)
            
            # Build model
            model = Sequential()
            
            # LSTM layers
            model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
            model.add(Dropout(0.2))
            model.add(BatchNormalization())
            
            model.add(LSTM(50, return_sequences=True))
            model.add(Dropout(0.2))
            model.add(BatchNormalization())
            
            model.add(LSTM(50))
            model.add(Dropout(0.2))
            model.add(BatchNormalization())
            
            # Output layer
            if target_variable in ['signal_direction', 'is_profitable']:
                num_classes = len(np.unique(y_train))
                if num_classes == 2:
                    model.add(Dense(1, activation='sigmoid'))
                    loss = 'binary_crossentropy'
                else:
                    model.add(Dense(num_classes, activation='softmax'))
                    loss = 'sparse_categorical_crossentropy'
            else:
                model.add(Dense(1))
                loss = 'mse'
            
            # Compile model
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss=loss,
                metrics=['accuracy'] if loss != 'mse' else ['mae']
            )
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5)
            ]
            
            # Train model
            history = model.fit(
                X_train_scaled, y_train,
                validation_data=(X_val_scaled, y_val),
                epochs=100,
                batch_size=32,
                callbacks=callbacks,
                verbose=0
            )
            
            return model, scaler
            
        except Exception as e:
            self.logger.error(f"Error training LSTM: {e}")
            raise e
    
    def _evaluate_model(self, model: Any, X_val: np.ndarray, y_val: np.ndarray, target_variable: str) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            metrics = {}
            
            # Make predictions
            if hasattr(model, 'predict_proba'):
                y_pred_proba = model.predict_proba(X_val)
                y_pred = model.predict(X_val)
            else:
                y_pred = model.predict(X_val)
                y_pred_proba = None
            
            # Classification metrics
            if target_variable in ['signal_direction', 'is_profitable']:
                metrics['accuracy'] = accuracy_score(y_val, y_pred)
                metrics['precision'] = precision_score(y_val, y_pred, average='weighted', zero_division=0)
                metrics['recall'] = recall_score(y_val, y_pred, average='weighted', zero_division=0)
                metrics['f1_score'] = f1_score(y_val, y_pred, average='weighted', zero_division=0)
                
                if y_pred_proba is not None and len(np.unique(y_val)) == 2:
                    metrics['auc_score'] = roc_auc_score(y_val, y_pred_proba[:, 1])
            
            # Regression metrics
            else:
                metrics['mse'] = mean_squared_error(y_val, y_pred)
                metrics['mae'] = mean_absolute_error(y_val, y_pred)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {}
    
    def _save_model(self, model: Any, scaler: StandardScaler, model_name: str) -> str:
        """Save trained model and scaler"""
        try:
            import os
            os.makedirs(self.models_dir, exist_ok=True)
            
            # Save model
            model_path = f"{self.models_dir}{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            
            if hasattr(model, 'save'):
                # Keras model
                model.save(model_path.replace('.pkl', '.h5'))
            else:
                # Sklearn/XGBoost/LightGBM model
                joblib.dump(model, model_path)
            
            # Save scaler
            scaler_path = model_path.replace('.pkl', '_scaler.pkl')
            joblib.dump(scaler, scaler_path)
            
            return model_path
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            raise e
    
    def walk_forward_validation(self, symbols: List[Symbol], model_type: str,
                               target_variable: str = 'signal_direction',
                               prediction_horizon_hours: int = 24,
                               training_window_days: int = 180,
                               validation_window_days: int = 30) -> Dict[str, Any]:
        """
        Perform walk-forward validation to prevent overfitting
        
        Args:
            symbols: List of symbols to validate
            model_type: Type of model to train
            target_variable: Target variable to predict
            prediction_horizon_hours: Hours ahead to predict
            training_window_days: Days of training data per fold
            validation_window_days: Days of validation data per fold
            
        Returns:
            Dictionary with validation results
        """
        try:
            self.logger.info(f"Starting walk-forward validation for {model_type}")
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=365)  # Total period
            
            results = {
                'folds': [],
                'overall_metrics': {},
                'model_performance': []
            }
            
            current_date = start_date + timedelta(days=training_window_days)
            
            fold_number = 0
            while current_date + timedelta(days=validation_window_days) <= end_date:
                fold_number += 1
                
                # Define fold periods
                fold_training_start = current_date - timedelta(days=training_window_days)
                fold_training_end = current_date
                fold_validation_start = current_date
                fold_validation_end = current_date + timedelta(days=validation_window_days)
                
                self.logger.info(f"Fold {fold_number}: Training {fold_training_start.date()} to {fold_training_end.date()}, "
                               f"Validation {fold_validation_start.date()} to {fold_validation_end.date()}")
                
                try:
                    # Train model on fold
                    model_name = f"walk_forward_{model_type}_fold_{fold_number}"
                    
                    if model_type == 'XGBOOST':
                        model = self.train_xgboost_model(symbols, model_name, target_variable, 
                                                       prediction_horizon_hours, training_window_days)
                    elif model_type == 'LIGHTGBM':
                        model = self.train_lightgbm_model(symbols, model_name, target_variable,
                                                        prediction_horizon_hours, training_window_days)
                    elif model_type == 'LSTM':
                        model = self.train_lstm_model(symbols, model_name, target_variable,
                                                    prediction_horizon_hours, training_window_days)
                    else:
                        raise ValueError(f"Unsupported model type: {model_type}")
                    
                    # Store fold results
                    fold_result = {
                        'fold_number': fold_number,
                        'training_period': f"{fold_training_start.date()} to {fold_training_end.date()}",
                        'validation_period': f"{fold_validation_start.date()} to {fold_validation_end.date()}",
                        'model_id': model.id,
                        'accuracy': model.accuracy,
                        'f1_score': model.f1_score,
                        'mse': model.mse,
                        'mae': model.mae
                    }
                    
                    results['folds'].append(fold_result)
                    results['model_performance'].append({
                        'fold': fold_number,
                        'accuracy': model.accuracy or 0,
                        'f1_score': model.f1_score or 0,
                        'mse': model.mse or 0,
                        'mae': model.mae or 0
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error in fold {fold_number}: {e}")
                    continue
                
                # Move to next fold
                current_date += timedelta(days=validation_window_days)
            
            # Calculate overall metrics
            if results['model_performance']:
                perf_df = pd.DataFrame(results['model_performance'])
                results['overall_metrics'] = {
                    'avg_accuracy': perf_df['accuracy'].mean(),
                    'std_accuracy': perf_df['accuracy'].std(),
                    'avg_f1_score': perf_df['f1_score'].mean(),
                    'std_f1_score': perf_df['f1_score'].std(),
                    'avg_mse': perf_df['mse'].mean(),
                    'std_mse': perf_df['mse'].std(),
                    'avg_mae': perf_df['mae'].mean(),
                    'std_mae': perf_df['mae'].std(),
                    'total_folds': len(results['folds'])
                }
            
            self.logger.info(f"Walk-forward validation completed: {len(results['folds'])} folds")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in walk-forward validation: {e}")
            raise e

