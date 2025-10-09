"""
Phase 5.4: ML Model Training & Integration Service
Implements CNN model training on chart images with entry points
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.conf import settings
import os
import json
import pickle

# ML Libraries
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, callbacks
    from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    import cv2
    from PIL import Image, ImageDraw, ImageFont
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available. Install tensorflow, sklearn, opencv-python, pillow")

from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import ChartImage, ChartPattern, EntryPoint, ChartMLModel, ChartMLPrediction

logger = logging.getLogger(__name__)


class MLModelTrainingService:
    """Service for training ML models on chart images with entry points"""
    
    def __init__(self):
        if not ML_AVAILABLE:
            raise ImportError("ML libraries not available. Please install required packages.")
        
        # Model configuration
        self.model_config = {
            'image_size': (224, 224, 3),  # Standard CNN input size
            'batch_size': 32,
            'epochs': 100,
            'learning_rate': 0.001,
            'validation_split': 0.2,
            'patience': 10,  # Early stopping patience
            'min_samples': 100  # Minimum samples per class
        }
        
        # Training data configuration
        self.data_config = {
            'min_confidence': 0.7,  # Minimum confidence for training data
            'balance_classes': True,  # Balance classes for training
            'augmentation': True,  # Use data augmentation
            'test_split': 0.2,  # Test set split
            'validation_split': 0.2  # Validation set split
        }
        
        # Model architectures
        self.model_architectures = {
            'simple_cnn': self._create_simple_cnn,
            'resnet_like': self._create_resnet_like,
            'attention_cnn': self._create_attention_cnn,
            'multi_task': self._create_multi_task_model
        }
    
    def prepare_training_data(self, symbols: Optional[List[Symbol]] = None) -> Dict[str, Any]:
        """
        Prepare training data from chart images and entry points
        
        Args:
            symbols: List of symbols to include (None for all)
            
        Returns:
            Dictionary with training data statistics
        """
        try:
            logger.info("Preparing training data for ML models...")
            
            # Get chart images with entry points
            chart_images = ChartImage.objects.filter(
                is_training_data=True,
                chartpattern__isnull=False,
                entrypoint__isnull=False
            ).distinct()
            
            if symbols:
                chart_images = chart_images.filter(symbol__in=symbols)
            
            if not chart_images.exists():
                logger.warning("No chart images with patterns and entry points found")
                return {'status': 'error', 'message': 'No training data available'}
            
            # Prepare data
            training_data = {
                'images': [],
                'labels': [],
                'entry_points': [],
                'patterns': [],
                'metadata': []
            }
            
            stats = {
                'total_charts': 0,
                'charts_with_entries': 0,
                'charts_with_patterns': 0,
                'total_entries': 0,
                'total_patterns': 0,
                'buy_entries': 0,
                'sell_entries': 0
            }
            
            for chart_image in chart_images:
                try:
                    stats['total_charts'] += 1
                    
                    # Get patterns for this chart
                    patterns = ChartPattern.objects.filter(
                        chart_image=chart_image,
                        confidence_score__gte=self.data_config['min_confidence']
                    )
                    
                    # Get entry points for this chart
                    entry_points = EntryPoint.objects.filter(
                        chart_image=chart_image,
                        confidence_score__gte=self.data_config['min_confidence']
                    )
                    
                    if patterns.exists():
                        stats['charts_with_patterns'] += 1
                        stats['total_patterns'] += patterns.count()
                    
                    if entry_points.exists():
                        stats['charts_with_entries'] += 1
                        stats['total_entries'] += entry_points.count()
                        
                        # Count by type
                        buy_entries = entry_points.filter(entry_type__in=['BUY', 'BUY_LIMIT', 'BUY_STOP'])
                        sell_entries = entry_points.filter(entry_type__in=['SELL', 'SELL_LIMIT', 'SELL_STOP'])
                        
                        stats['buy_entries'] += buy_entries.count()
                        stats['sell_entries'] += sell_entries.count()
                        
                        # Process each entry point
                        for entry_point in entry_points:
                            try:
                                # Load and process image
                                image_data = self._process_chart_image(chart_image, entry_point)
                                
                                if image_data is not None:
                                    training_data['images'].append(image_data['image'])
                                    training_data['labels'].append(image_data['label'])
                                    training_data['entry_points'].append({
                                        'entry_type': entry_point.entry_type,
                                        'confidence_score': entry_point.confidence_score,
                                        'entry_price': float(entry_point.entry_price),
                                        'stop_loss': float(entry_point.stop_loss) if entry_point.stop_loss else None,
                                        'take_profit': float(entry_point.take_profit) if entry_point.take_profit else None,
                                        'risk_reward_ratio': entry_point.risk_reward_ratio
                                    })
                                    training_data['patterns'].append([
                                        {
                                            'pattern_type': p.pattern_type,
                                            'confidence_score': p.confidence_score,
                                            'strength': p.strength
                                        } for p in patterns
                                    ])
                                    training_data['metadata'].append({
                                        'symbol': chart_image.symbol.symbol,
                                        'timeframe': chart_image.timeframe,
                                        'chart_type': chart_image.chart_type,
                                        'start_time': chart_image.start_time.isoformat(),
                                        'end_time': chart_image.end_time.isoformat()
                                    })
                            
                            except Exception as e:
                                logger.error(f"Error processing entry point {entry_point.id}: {e}")
                
                except Exception as e:
                    logger.error(f"Error processing chart {chart_image.id}: {e}")
            
            # Convert to numpy arrays
            if training_data['images']:
                training_data['images'] = np.array(training_data['images'])
                training_data['labels'] = np.array(training_data['labels'])
                
                # Balance classes if requested
                if self.data_config['balance_classes']:
                    training_data = self._balance_classes(training_data)
                
                stats['final_samples'] = len(training_data['images'])
                stats['class_distribution'] = self._get_class_distribution(training_data['labels'])
                
                logger.info(f"Training data prepared: {stats['final_samples']} samples")
                return {
                    'status': 'success',
                    'data': training_data,
                    'stats': stats
                }
            else:
                return {
                    'status': 'error',
                    'message': 'No valid training samples found'
                }
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def train_model(self, model_name: str, architecture: str = 'simple_cnn', 
                   training_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Train ML model on chart images
        
        Args:
            model_name: Name for the model
            architecture: Model architecture to use
            training_data: Pre-prepared training data
            
        Returns:
            Dictionary with training results
        """
        try:
            logger.info(f"Training {architecture} model: {model_name}")
            
            # Prepare training data if not provided
            if training_data is None:
                data_result = self.prepare_training_data()
                if data_result['status'] != 'success':
                    return data_result
                training_data = data_result['data']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                training_data['images'],
                training_data['labels'],
                test_size=self.data_config['test_split'],
                random_state=42,
                stratify=training_data['labels']
            )
            
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train,
                test_size=self.data_config['validation_split'],
                random_state=42,
                stratify=y_train
            )
            
            # Create model
            if architecture not in self.model_architectures:
                raise ValueError(f"Unknown architecture: {architecture}")
            
            model = self.model_architectures[architecture]()
            
            # Compile model
            model.compile(
                optimizer=optimizers.Adam(learning_rate=self.model_config['learning_rate']),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Data augmentation
            if self.data_config['augmentation']:
                train_datagen = ImageDataGenerator(
                    rotation_range=10,
                    width_shift_range=0.1,
                    height_shift_range=0.1,
                    horizontal_flip=True,
                    zoom_range=0.1,
                    fill_mode='nearest'
                )
            else:
                train_datagen = ImageDataGenerator()
            
            # Callbacks
            callbacks_list = [
                callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=self.model_config['patience'],
                    restore_best_weights=True
                ),
                callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7
                ),
                callbacks.ModelCheckpoint(
                    filepath=os.path.join(settings.MEDIA_ROOT, 'models', f'{model_name}_best.h5'),
                    monitor='val_accuracy',
                    save_best_only=True,
                    save_weights_only=False
                )
            ]
            
            # Train model
            history = model.fit(
                train_datagen.flow(X_train, y_train, batch_size=self.model_config['batch_size']),
                steps_per_epoch=len(X_train) // self.model_config['batch_size'],
                epochs=self.model_config['epochs'],
                validation_data=(X_val, y_val),
                callbacks=callbacks_list,
                verbose=1
            )
            
            # Evaluate model
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
            y_pred = model.predict(X_test)
            y_pred_classes = np.argmax(y_pred, axis=1)
            
            # Calculate metrics
            metrics = {
                'test_accuracy': test_accuracy,
                'test_loss': test_loss,
                'classification_report': classification_report(y_test, y_pred_classes, output_dict=True),
                'confusion_matrix': confusion_matrix(y_test, y_pred_classes).tolist()
            }
            
            # Save model
            model_path = os.path.join(settings.MEDIA_ROOT, 'models', f'{model_name}.h5')
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            model.save(model_path)
            
            # Create ChartMLModel record
            chart_model = ChartMLModel.objects.create(
                name=model_name,
                model_type=architecture.upper(),
                version='1.0',
                status='TRAINED',
                target_task='ENTRY_POINT_DETECTION',
                prediction_horizon='REALTIME',
                accuracy_score=test_accuracy,
                precision_score=metrics['classification_report']['macro avg']['precision'],
                recall_score=metrics['classification_report']['macro avg']['recall'],
                f1_score=metrics['classification_report']['macro avg']['f1-score'],
                model_file_path=model_path,
                training_data_size=len(training_data['images']),
                training_parameters=json.dumps(self.model_config),
                is_active=True
            )
            
            logger.info(f"Model {model_name} trained successfully with accuracy: {test_accuracy:.4f}")
            
            return {
                'status': 'success',
                'model_id': chart_model.id,
                'model_name': model_name,
                'accuracy': test_accuracy,
                'metrics': metrics,
                'history': history.history,
                'model_path': model_path
            }
            
        except Exception as e:
            logger.error(f"Error training model {model_name}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def evaluate_model(self, model_id: int, test_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate a trained model
        
        Args:
            model_id: ID of the model to evaluate
            test_data: Test data (if not provided, will use validation split)
            
        Returns:
            Dictionary with evaluation results
        """
        try:
            logger.info(f"Evaluating model {model_id}")
            
            # Get model
            chart_model = ChartMLModel.objects.get(id=model_id)
            if not chart_model.model_file_path or not os.path.exists(chart_model.model_file_path):
                return {'status': 'error', 'message': 'Model file not found'}
            
            # Load model
            model = keras.models.load_model(chart_model.model_file_path)
            
            # Prepare test data if not provided
            if test_data is None:
                data_result = self.prepare_training_data()
                if data_result['status'] != 'success':
                    return data_result
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    data_result['data']['images'],
                    data_result['data']['labels'],
                    test_size=self.data_config['test_split'],
                    random_state=42,
                    stratify=data_result['data']['labels']
                )
            else:
                X_test = test_data['images']
                y_test = test_data['labels']
            
            # Evaluate model
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
            y_pred = model.predict(X_test)
            y_pred_classes = np.argmax(y_pred, axis=1)
            
            # Calculate detailed metrics
            metrics = {
                'test_accuracy': test_accuracy,
                'test_loss': test_loss,
                'classification_report': classification_report(y_test, y_pred_classes, output_dict=True),
                'confusion_matrix': confusion_matrix(y_test, y_pred_classes).tolist(),
                'precision': metrics['classification_report']['macro avg']['precision'],
                'recall': metrics['classification_report']['macro avg']['recall'],
                'f1_score': metrics['classification_report']['macro avg']['f1-score']
            }
            
            # Update model record
            chart_model.accuracy_score = test_accuracy
            chart_model.precision_score = metrics['precision']
            chart_model.recall_score = metrics['recall']
            chart_model.f1_score = metrics['f1_score']
            chart_model.last_evaluated_at = timezone.now()
            chart_model.save()
            
            logger.info(f"Model {model_id} evaluated with accuracy: {test_accuracy:.4f}")
            
            return {
                'status': 'success',
                'model_id': model_id,
                'metrics': metrics,
                'predictions': y_pred_classes.tolist(),
                'true_labels': y_test.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model {model_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def predict_entry_points(self, chart_image: ChartImage, model_id: int) -> Dict[str, Any]:
        """
        Predict entry points for a chart image using trained model
        
        Args:
            chart_image: Chart image to analyze
            model_id: ID of the model to use
            
        Returns:
            Dictionary with predictions
        """
        try:
            logger.info(f"Predicting entry points for chart {chart_image.id} using model {model_id}")
            
            # Get model
            chart_model = ChartMLModel.objects.get(id=model_id)
            if not chart_model.model_file_path or not os.path.exists(chart_model.model_file_path):
                return {'status': 'error', 'message': 'Model file not found'}
            
            # Load model
            model = keras.models.load_model(chart_model.model_file_path)
            
            # Process chart image
            image_data = self._process_chart_image_for_prediction(chart_image)
            if image_data is None:
                return {'status': 'error', 'message': 'Could not process chart image'}
            
            # Make prediction
            prediction = model.predict(np.expand_dims(image_data, axis=0))
            predicted_class = np.argmax(prediction[0])
            confidence = float(np.max(prediction[0]))
            
            # Map prediction to entry type
            entry_type = self._map_prediction_to_entry_type(predicted_class)
            
            # Create prediction record
            chart_prediction = ChartMLPrediction.objects.create(
                chart_image=chart_image,
                model=chart_model,
                prediction_type='ENTRY_POINT',
                predicted_value=entry_type,
                confidence_score=confidence,
                prediction_details=json.dumps({
                    'predicted_class': int(predicted_class),
                    'all_probabilities': prediction[0].tolist(),
                    'model_version': chart_model.version
                }),
                is_validated=False
            )
            
            logger.info(f"Prediction completed: {entry_type} with confidence {confidence:.4f}")
            
            return {
                'status': 'success',
                'prediction_id': chart_prediction.id,
                'entry_type': entry_type,
                'confidence': confidence,
                'all_probabilities': prediction[0].tolist(),
                'model_name': chart_model.name
            }
            
        except Exception as e:
            logger.error(f"Error predicting entry points: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_chart_image(self, chart_image: ChartImage, entry_point: EntryPoint) -> Optional[Dict[str, Any]]:
        """Process chart image for training"""
        try:
            # Load image
            image_path = chart_image.image_file.path
            if not os.path.exists(image_path):
                return None
            
            image = load_img(image_path, target_size=self.model_config['image_size'][:2])
            image_array = img_to_array(image)
            
            # Normalize image
            image_array = image_array / 255.0
            
            # Create label based on entry type
            if entry_point.entry_type in ['BUY', 'BUY_LIMIT', 'BUY_STOP']:
                label = 0  # Buy
            elif entry_point.entry_type in ['SELL', 'SELL_LIMIT', 'SELL_STOP']:
                label = 1  # Sell
            else:
                label = 2  # Hold/Unknown
            
            return {
                'image': image_array,
                'label': label
            }
            
        except Exception as e:
            logger.error(f"Error processing chart image: {e}")
            return None
    
    def _process_chart_image_for_prediction(self, chart_image: ChartImage) -> Optional[np.ndarray]:
        """Process chart image for prediction"""
        try:
            # Load image
            image_path = chart_image.image_file.path
            if not os.path.exists(image_path):
                return None
            
            image = load_img(image_path, target_size=self.model_config['image_size'][:2])
            image_array = img_to_array(image)
            
            # Normalize image
            image_array = image_array / 255.0
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error processing chart image for prediction: {e}")
            return None
    
    def _create_simple_cnn(self):
        """Create simple CNN architecture"""
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.model_config['image_size']),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(3, activation='softmax')  # Buy, Sell, Hold
        ])
        return model
    
    def _create_resnet_like(self):
        """Create ResNet-like architecture"""
        inputs = keras.Input(shape=self.model_config['image_size'])
        
        # Initial convolution
        x = layers.Conv2D(64, (7, 7), strides=2, padding='same')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((3, 3), strides=2, padding='same')(x)
        
        # Residual blocks
        for i in range(3):
            x = self._residual_block(x, 64)
        
        for i in range(4):
            x = self._residual_block(x, 128)
        
        for i in range(6):
            x = self._residual_block(x, 256)
        
        # Global average pooling and classification
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        outputs = layers.Dense(3, activation='softmax')(x)
        
        model = models.Model(inputs, outputs)
        return model
    
    def _residual_block(self, x, filters):
        """Create residual block"""
        shortcut = x
        
        x = layers.Conv2D(filters, (3, 3), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        
        x = layers.Conv2D(filters, (3, 3), padding='same')(x)
        x = layers.BatchNormalization()(x)
        
        # Add shortcut connection
        if shortcut.shape[-1] != filters:
            shortcut = layers.Conv2D(filters, (1, 1))(shortcut)
        
        x = layers.Add()([x, shortcut])
        x = layers.Activation('relu')(x)
        
        return x
    
    def _create_attention_cnn(self):
        """Create CNN with attention mechanism"""
        inputs = keras.Input(shape=self.model_config['image_size'])
        
        # Feature extraction
        x = layers.Conv2D(32, (3, 3), activation='relu')(inputs)
        x = layers.MaxPooling2D((2, 2))(x)
        
        x = layers.Conv2D(64, (3, 3), activation='relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        
        x = layers.Conv2D(128, (3, 3), activation='relu')(x)
        
        # Attention mechanism
        attention = layers.Conv2D(1, (1, 1), activation='sigmoid')(x)
        x = layers.Multiply()([x, attention])
        
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        outputs = layers.Dense(3, activation='softmax')(x)
        
        model = models.Model(inputs, outputs)
        return model
    
    def _create_multi_task_model(self):
        """Create multi-task model for pattern and entry detection"""
        inputs = keras.Input(shape=self.model_config['image_size'])
        
        # Shared feature extraction
        x = layers.Conv2D(32, (3, 3), activation='relu')(inputs)
        x = layers.MaxPooling2D((2, 2))(x)
        
        x = layers.Conv2D(64, (3, 3), activation='relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        
        x = layers.Conv2D(128, (3, 3), activation='relu')(x)
        x = layers.GlobalAveragePooling2D()(x)
        
        # Task-specific heads
        entry_head = layers.Dense(64, activation='relu')(x)
        entry_head = layers.Dropout(0.5)(entry_head)
        entry_output = layers.Dense(3, activation='softmax', name='entry_prediction')(entry_head)
        
        pattern_head = layers.Dense(64, activation='relu')(x)
        pattern_head = layers.Dropout(0.5)(pattern_head)
        pattern_output = layers.Dense(5, activation='softmax', name='pattern_prediction')(pattern_head)  # 5 pattern types
        
        model = models.Model(inputs, [entry_output, pattern_output])
        return model
    
    def _balance_classes(self, training_data: Dict) -> Dict:
        """Balance classes in training data"""
        try:
            labels = training_data['labels']
            unique_labels, counts = np.unique(labels, return_counts=True)
            
            # Find minimum count
            min_count = min(counts)
            
            # Balance each class
            balanced_indices = []
            for label in unique_labels:
                label_indices = np.where(labels == label)[0]
                if len(label_indices) > min_count:
                    # Randomly sample min_count indices
                    selected_indices = np.random.choice(label_indices, min_count, replace=False)
                else:
                    selected_indices = label_indices
                balanced_indices.extend(selected_indices)
            
            # Create balanced dataset
            balanced_data = {
                'images': training_data['images'][balanced_indices],
                'labels': training_data['labels'][balanced_indices],
                'entry_points': [training_data['entry_points'][i] for i in balanced_indices],
                'patterns': [training_data['patterns'][i] for i in balanced_indices],
                'metadata': [training_data['metadata'][i] for i in balanced_indices]
            }
            
            return balanced_data
            
        except Exception as e:
            logger.error(f"Error balancing classes: {e}")
            return training_data
    
    def _get_class_distribution(self, labels: np.ndarray) -> Dict[str, int]:
        """Get class distribution"""
        unique_labels, counts = np.unique(labels, return_counts=True)
        class_names = ['Buy', 'Sell', 'Hold']
        
        distribution = {}
        for i, (label, count) in enumerate(zip(unique_labels, counts)):
            if i < len(class_names):
                distribution[class_names[i]] = int(count)
        
        return distribution
    
    def _map_prediction_to_entry_type(self, predicted_class: int) -> str:
        """Map prediction class to entry type"""
        mapping = {
            0: 'BUY',
            1: 'SELL',
            2: 'HOLD'
        }
        return mapping.get(predicted_class, 'HOLD')

