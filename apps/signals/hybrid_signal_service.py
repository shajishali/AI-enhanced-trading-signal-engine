"""
Phase 4 Hybrid Signal Fusion Service
Fuses rule-based signals with ML predictions for enhanced accuracy
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from apps.signals.models import (
    TradingSignal, MLModel, MLPrediction, SignalType, SignalFactor
)
from apps.signals.services import SignalGenerationService
from apps.signals.ml_inference_service import MLInferenceService
from apps.trading.models import Symbol
from apps.data.models import MarketData

logger = logging.getLogger(__name__)


class HybridSignalService:
    """Service for fusing rule-based and ML signals"""
    
    def __init__(self):
        self.logger = logger
        self.signal_service = SignalGenerationService()
        self.ml_service = MLInferenceService()
        
        # Hybrid configuration
        self.config = {
            'min_ml_confidence': 0.6,  # Minimum ML confidence threshold
            'min_rule_strength': 0.5,  # Minimum rule-based signal strength
            'fusion_weight_ml': 0.6,   # Weight for ML predictions
            'fusion_weight_rule': 0.4,  # Weight for rule-based signals
            'position_size_multiplier': 1.5,  # ML confidence multiplier for position sizing
            'retrain_frequency_days': 7,  # Retrain ML models every 7 days
        }
    
    def generate_hybrid_signal(self, symbol: Symbol, 
                             signal_type: str = 'BUY',
                             timeframe: str = '1h',
                             force_generation: bool = False) -> Optional[Dict[str, Any]]:
        """
        Generate hybrid signal combining rule-based and ML predictions
        
        Args:
            symbol: Symbol to generate signal for
            signal_type: Type of signal (BUY, SELL, HOLD)
            timeframe: Timeframe for the signal
            force_generation: Force signal generation even if conditions not met
            
        Returns:
            Dictionary with hybrid signal data
        """
        try:
            self.logger.info(f"Generating hybrid signal for {symbol.symbol} ({signal_type})")
            
            # Step 1: Generate rule-based signal
            rule_signal = self._generate_rule_based_signal(symbol, signal_type, timeframe)
            
            # Step 2: Get ML prediction
            ml_prediction = self._get_ml_prediction(symbol, signal_type)
            
            # Step 3: Fuse signals
            hybrid_signal = self._fuse_signals(rule_signal, ml_prediction, symbol, signal_type)
            
            # Step 4: Apply hybrid logic
            if not force_generation and not self._should_generate_signal(hybrid_signal):
                self.logger.info(f"Hybrid conditions not met for {symbol.symbol}")
                return None
            
            # Step 5: Calculate position sizing
            position_size = self._calculate_position_size(hybrid_signal, symbol)
            
            # Step 6: Create final hybrid signal
            final_signal = self._create_hybrid_signal(
                symbol, signal_type, timeframe, hybrid_signal, position_size
            )
            
            self.logger.info(f"✓ Hybrid signal generated for {symbol.symbol}: {final_signal['strength']:.2f}")
            return final_signal
            
        except Exception as e:
            self.logger.error(f"Error generating hybrid signal for {symbol.symbol}: {e}")
            return None
    
    def _generate_rule_based_signal(self, symbol: Symbol, signal_type: str, timeframe: str) -> Dict[str, Any]:
        """Generate rule-based signal using existing signal generation service"""
        try:
            # Get recent signals for the symbol
            recent_signals = TradingSignal.objects.filter(
                symbol=symbol,
                signal_type__name=signal_type,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')
            
            if recent_signals.exists():
                latest_signal = recent_signals.first()
                
                # Calculate rule-based strength from signal factors
                rule_strength = self._calculate_rule_strength(latest_signal)
                
                return {
                    'signal': latest_signal,
                    'strength': rule_strength,
                    'confidence': latest_signal.confidence_score or 0.5,
                    'factors': self._get_signal_factors(latest_signal),
                    'timestamp': latest_signal.created_at,
                    'source': 'rule_based'
                }
            else:
                # Generate new rule-based signal
                signals = self.signal_service.generate_signals_for_symbol(symbol)
                
                if signals:
                    signal = signals[0]  # Get first generated signal
                    rule_strength = self._calculate_rule_strength(signal)
                    
                    return {
                        'signal': signal,
                        'strength': rule_strength,
                        'confidence': signal.confidence_score or 0.5,
                        'factors': self._get_signal_factors(signal),
                        'timestamp': signal.created_at,
                        'source': 'rule_based'
                    }
                else:
                    return {
                        'signal': None,
                        'strength': 0.0,
                        'confidence': 0.0,
                        'factors': [],
                        'timestamp': timezone.now(),
                        'source': 'rule_based'
                    }
                    
        except Exception as e:
            self.logger.error(f"Error generating rule-based signal: {e}")
            return {
                'signal': None,
                'strength': 0.0,
                'confidence': 0.0,
                'factors': [],
                'timestamp': timezone.now(),
                'source': 'rule_based'
            }
    
    def _get_ml_prediction(self, symbol: Symbol, signal_type: str) -> Dict[str, Any]:
        """Get ML prediction for the symbol"""
        try:
            # Get the best active ML model for signal direction
            model = MLModel.objects.filter(
                target_variable='signal_direction',
                is_active=True,
                status='DEPLOYED'
            ).order_by('-performance_score').first()
            
            if not model:
                self.logger.warning("No active ML model found for signal direction")
                return {
                    'prediction': 0,  # Neutral
                    'confidence': 0.0,
                    'probabilities': {'buy': 0.33, 'sell': 0.33, 'hold': 0.34},
                    'model': None,
                    'source': 'ml'
                }
            
            # Get ML prediction
            prediction_result = self.ml_service.predict_signal_direction(
                symbol=symbol,
                model_name=model.name,
                prediction_horizon_hours=24
            )
            
            # Convert prediction to signal strength
            prediction_value = prediction_result['prediction']
            confidence = prediction_result['confidence']
            
            # Map prediction to signal strength
            if signal_type == 'BUY':
                if prediction_value > 0:
                    ml_strength = min(1.0, prediction_value * confidence)
                else:
                    ml_strength = max(0.0, prediction_value * confidence)
            elif signal_type == 'SELL':
                if prediction_value < 0:
                    ml_strength = min(1.0, abs(prediction_value) * confidence)
                else:
                    ml_strength = max(0.0, abs(prediction_value) * confidence)
            else:  # HOLD
                ml_strength = 0.5  # Neutral strength
            
            return {
                'prediction': prediction_value,
                'confidence': confidence,
                'probabilities': prediction_result.get('probabilities', {}),
                'strength': ml_strength,
                'model': model,
                'source': 'ml'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ML prediction: {e}")
            return {
                'prediction': 0,
                'confidence': 0.0,
                'probabilities': {'buy': 0.33, 'sell': 0.33, 'hold': 0.34},
                'strength': 0.0,
                'model': None,
                'source': 'ml'
            }
    
    def _fuse_signals(self, rule_signal: Dict[str, Any], ml_prediction: Dict[str, Any], 
                     symbol: Symbol, signal_type: str) -> Dict[str, Any]:
        """Fuse rule-based and ML signals"""
        try:
            # Extract strengths and confidences
            rule_strength = rule_signal['strength']
            rule_confidence = rule_signal['confidence']
            ml_strength = ml_prediction['strength']
            ml_confidence = ml_prediction['confidence']
            
            # Weighted fusion
            ml_weight = self.config['fusion_weight_ml']
            rule_weight = self.config['fusion_weight_rule']
            
            # Adjust weights based on confidence
            if ml_confidence < self.config['min_ml_confidence']:
                ml_weight = 0.2  # Reduce ML weight if low confidence
                rule_weight = 0.8
            
            if rule_confidence < self.config['min_rule_strength']:
                rule_weight = 0.2  # Reduce rule weight if low confidence
                ml_weight = 0.8
            
            # Normalize weights
            total_weight = ml_weight + rule_weight
            ml_weight /= total_weight
            rule_weight /= total_weight
            
            # Calculate fused strength
            fused_strength = (ml_strength * ml_weight) + (rule_strength * rule_weight)
            
            # Calculate fused confidence
            fused_confidence = (ml_confidence * ml_weight) + (rule_confidence * rule_weight)
            
            # Determine agreement level
            agreement_level = self._calculate_agreement_level(rule_signal, ml_prediction)
            
            return {
                'fused_strength': fused_strength,
                'fused_confidence': fused_confidence,
                'rule_strength': rule_strength,
                'rule_confidence': rule_confidence,
                'ml_strength': ml_strength,
                'ml_confidence': ml_confidence,
                'ml_weight': ml_weight,
                'rule_weight': rule_weight,
                'agreement_level': agreement_level,
                'rule_signal': rule_signal,
                'ml_prediction': ml_prediction,
                'symbol': symbol,
                'signal_type': signal_type
            }
            
        except Exception as e:
            self.logger.error(f"Error fusing signals: {e}")
            return {
                'fused_strength': 0.0,
                'fused_confidence': 0.0,
                'agreement_level': 0.0,
                'rule_signal': rule_signal,
                'ml_prediction': ml_prediction,
                'symbol': symbol,
                'signal_type': signal_type
            }
    
    def _should_generate_signal(self, hybrid_signal: Dict[str, Any]) -> bool:
        """Determine if hybrid signal should be generated based on fusion criteria"""
        try:
            fused_strength = hybrid_signal['fused_strength']
            fused_confidence = hybrid_signal['fused_confidence']
            agreement_level = hybrid_signal['agreement_level']
            
            # Criteria for signal generation
            criteria = [
                fused_strength >= 0.6,  # Minimum fused strength
                fused_confidence >= 0.7,  # Minimum fused confidence
                agreement_level >= 0.5,  # Minimum agreement between rule and ML
            ]
            
            # All criteria must be met
            return all(criteria)
            
        except Exception as e:
            self.logger.error(f"Error checking signal generation criteria: {e}")
            return False
    
    def _calculate_position_size(self, hybrid_signal: Dict[str, Any], symbol: Symbol) -> float:
        """Calculate position size based on hybrid signal strength and ML confidence"""
        try:
            fused_strength = hybrid_signal['fused_strength']
            fused_confidence = hybrid_signal['fused_confidence']
            ml_confidence = hybrid_signal['ml_confidence']
            
            # Base position size
            base_position_size = 1.0
            
            # Adjust based on fused strength
            strength_multiplier = fused_strength
            
            # Adjust based on ML confidence
            ml_multiplier = 1.0 + (ml_confidence - 0.5) * self.config['position_size_multiplier']
            
            # Calculate final position size
            position_size = base_position_size * strength_multiplier * ml_multiplier
            
            # Cap position size
            position_size = min(position_size, 2.0)  # Maximum 2x position size
            position_size = max(position_size, 0.1)  # Minimum 0.1x position size
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 1.0
    
    def _create_hybrid_signal(self, symbol: Symbol, signal_type: str, timeframe: str,
                            hybrid_signal: Dict[str, Any], position_size: float) -> Dict[str, Any]:
        """Create final hybrid signal with all metadata"""
        try:
            # Get signal type object
            signal_type_obj = SignalType.objects.get(name=signal_type)
            
            # Create hybrid signal record
            hybrid_signal_record = TradingSignal.objects.create(
                symbol=symbol,
                signal_type=signal_type_obj,
                timeframe=timeframe,
                price=symbol.current_price or 0,
                confidence_score=hybrid_signal['fused_confidence'],
                strength_score=hybrid_signal['fused_strength'],
                is_hybrid=True,  # Mark as hybrid signal
                metadata={
                    'rule_strength': hybrid_signal['rule_strength'],
                    'rule_confidence': hybrid_signal['rule_confidence'],
                    'ml_strength': hybrid_signal['ml_strength'],
                    'ml_confidence': hybrid_signal['ml_confidence'],
                    'ml_weight': hybrid_signal['ml_weight'],
                    'rule_weight': hybrid_signal['rule_weight'],
                    'agreement_level': hybrid_signal['agreement_level'],
                    'position_size': position_size,
                    'ml_model': hybrid_signal['ml_prediction']['model'].name if hybrid_signal['ml_prediction']['model'] else None,
                    'fusion_method': 'weighted_average'
                }
            )
            
            return {
                'id': hybrid_signal_record.id,
                'symbol': symbol.symbol,
                'signal_type': signal_type,
                'timeframe': timeframe,
                'price': hybrid_signal_record.price,
                'strength': hybrid_signal['fused_strength'],
                'confidence': hybrid_signal['fused_confidence'],
                'position_size': position_size,
                'agreement_level': hybrid_signal['agreement_level'],
                'rule_strength': hybrid_signal['rule_strength'],
                'ml_strength': hybrid_signal['ml_strength'],
                'ml_model': hybrid_signal['ml_prediction']['model'].name if hybrid_signal['ml_prediction']['model'] else None,
                'created_at': hybrid_signal_record.created_at.isoformat(),
                'is_hybrid': True
            }
            
        except Exception as e:
            self.logger.error(f"Error creating hybrid signal: {e}")
            return {}
    
    def _calculate_rule_strength(self, signal: TradingSignal) -> float:
        """Calculate rule-based signal strength from signal factors"""
        try:
            if not signal:
                return 0.0
            
            # Get signal factors
            factors = signal.signal_factor_contributions.all()
            
            if not factors.exists():
                return signal.strength_score or 0.5
            
            # Calculate weighted strength
            total_weight = 0
            weighted_strength = 0
            
            for factor in factors:
                weight = factor.weight or 1.0
                strength = factor.contribution_score or 0.5
                
                total_weight += weight
                weighted_strength += strength * weight
            
            if total_weight > 0:
                return weighted_strength / total_weight
            else:
                return signal.strength_score or 0.5
                
        except Exception as e:
            self.logger.error(f"Error calculating rule strength: {e}")
            return 0.5
    
    def _get_signal_factors(self, signal: TradingSignal) -> List[Dict[str, Any]]:
        """Get signal factors for analysis"""
        try:
            factors = []
            for factor in signal.signal_factor_contributions.all():
                factors.append({
                    'factor_name': factor.factor.name,
                    'weight': factor.weight,
                    'contribution': factor.contribution_score,
                    'description': factor.factor.description
                })
            return factors
        except Exception as e:
            self.logger.error(f"Error getting signal factors: {e}")
            return []
    
    def _calculate_agreement_level(self, rule_signal: Dict[str, Any], ml_prediction: Dict[str, Any]) -> float:
        """Calculate agreement level between rule-based and ML signals"""
        try:
            rule_strength = rule_signal['strength']
            ml_strength = ml_prediction['strength']
            
            # Calculate agreement based on strength similarity
            strength_diff = abs(rule_strength - ml_strength)
            agreement = 1.0 - strength_diff
            
            # Boost agreement if both signals are strong in same direction
            if rule_strength > 0.6 and ml_strength > 0.6:
                agreement += 0.2
            elif rule_strength < 0.4 and ml_strength < 0.4:
                agreement += 0.2
            
            return min(1.0, max(0.0, agreement))
            
        except Exception as e:
            self.logger.error(f"Error calculating agreement level: {e}")
            return 0.0
    
    def get_hybrid_signal_summary(self, symbol: Symbol, days: int = 7) -> Dict[str, Any]:
        """Get summary of hybrid signals for a symbol"""
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Get hybrid signals
            hybrid_signals = TradingSignal.objects.filter(
                symbol=symbol,
                is_hybrid=True,
                created_at__gte=start_date
            ).order_by('-created_at')
            
            if not hybrid_signals.exists():
                return {
                    'total_signals': 0,
                    'avg_strength': 0.0,
                    'avg_confidence': 0.0,
                    'avg_agreement': 0.0,
                    'ml_model_usage': {},
                    'signal_types': {}
                }
            
            # Calculate statistics
            total_signals = hybrid_signals.count()
            strengths = [s.strength_score or 0 for s in hybrid_signals]
            confidences = [s.confidence_score or 0 for s in hybrid_signals]
            
            # Extract agreement levels from metadata
            agreements = []
            ml_models = {}
            signal_types = {}
            
            for signal in hybrid_signals:
                metadata = signal.metadata or {}
                agreement = metadata.get('agreement_level', 0.0)
                agreements.append(agreement)
                
                ml_model = metadata.get('ml_model')
                if ml_model:
                    ml_models[ml_model] = ml_models.get(ml_model, 0) + 1
                
                signal_type = signal.signal_type.name
                signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            return {
                'total_signals': total_signals,
                'avg_strength': sum(strengths) / len(strengths) if strengths else 0.0,
                'avg_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
                'avg_agreement': sum(agreements) / len(agreements) if agreements else 0.0,
                'ml_model_usage': ml_models,
                'signal_types': signal_types,
                'recent_signals': [
                    {
                        'id': s.id,
                        'signal_type': s.signal_type.name,
                        'strength': s.strength_score,
                        'confidence': s.confidence_score,
                        'agreement': s.metadata.get('agreement_level', 0.0) if s.metadata else 0.0,
                        'created_at': s.created_at.isoformat()
                    }
                    for s in hybrid_signals[:10]  # Last 10 signals
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting hybrid signal summary: {e}")
            return {}
    
    def retrain_ml_models(self) -> Dict[str, Any]:
        """Retrain ML models with new data"""
        try:
            self.logger.info("Starting ML model retraining...")
            
            # Get models that need retraining
            models_to_retrain = MLModel.objects.filter(
                is_active=True,
                status='DEPLOYED',
                deployed_at__lte=timezone.now() - timedelta(days=self.config['retrain_frequency_days'])
            )
            
            retraining_results = {}
            
            for model in models_to_retrain:
                try:
                    # Import training service
                    from apps.signals.ml_training_service import MLTrainingService
                    
                    training_service = MLTrainingService()
                    
                    # Get symbols used in this model
                    symbols = Symbol.objects.filter(is_active=True)[:3]  # Use top 3 symbols
                    
                    # Retrain model
                    if model.model_type == 'XGBOOST':
                        new_model = training_service.train_xgboost_model(
                            symbols=symbols,
                            model_name=f"{model.name}_retrained_{datetime.now().strftime('%Y%m%d')}",
                            target_variable=model.target_variable,
                            prediction_horizon_hours=model.prediction_horizon,
                            training_days=180
                        )
                    elif model.model_type == 'LIGHTGBM':
                        new_model = training_service.train_lightgbm_model(
                            symbols=symbols,
                            model_name=f"{model.name}_retrained_{datetime.now().strftime('%Y%m%d')}",
                            target_variable=model.target_variable,
                            prediction_horizon_hours=model.prediction_horizon,
                            training_days=180
                        )
                    elif model.model_type == 'LSTM':
                        new_model = training_service.train_lstm_model(
                            symbols=symbols,
                            model_name=f"{model.name}_retrained_{datetime.now().strftime('%Y%m%d')}",
                            target_variable=model.target_variable,
                            prediction_horizon_hours=model.prediction_horizon,
                            training_days=180
                        )
                    else:
                        continue
                    
                    # Compare performance
                    if new_model.accuracy and new_model.accuracy > (model.accuracy or 0):
                        # New model is better, deploy it
                        model.is_active = False
                        model.save()
                        
                        new_model.status = 'DEPLOYED'
                        new_model.is_active = True
                        new_model.deployed_at = timezone.now()
                        new_model.save()
                        
                        retraining_results[model.name] = {
                            'status': 'replaced',
                            'old_accuracy': model.accuracy,
                            'new_accuracy': new_model.accuracy,
                            'improvement': new_model.accuracy - (model.accuracy or 0)
                        }
                    else:
                        # New model is not better, keep old one
                        retraining_results[model.name] = {
                            'status': 'kept_old',
                            'old_accuracy': model.accuracy,
                            'new_accuracy': new_model.accuracy,
                            'reason': 'No improvement'
                        }
                        
                except Exception as e:
                    retraining_results[model.name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            self.logger.info(f"ML model retraining completed: {retraining_results}")
            return retraining_results
            
        except Exception as e:
            self.logger.error(f"Error retraining ML models: {e}")
            return {'error': str(e)}

