"""
Phase 5.4: ML Integration Service
Integrates ML models with existing signal generation system
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from django.db import transaction

from apps.trading.models import Symbol
from apps.data.models import MarketData, TechnicalIndicator
from apps.signals.models import (
    ChartImage, ChartPattern, EntryPoint, ChartMLModel, ChartMLPrediction,
    TradingSignal, SignalHistory
)
from apps.signals.services import SignalGenerationService
from apps.signals.multi_timeframe_entry_detection_service import MultiTimeframeEntryDetectionService

logger = logging.getLogger(__name__)


class MLIntegrationService:
    """Service for integrating ML models with signal generation"""
    
    def __init__(self):
        self.signal_service = SignalGenerationService()
        self.entry_service = MultiTimeframeEntryDetectionService()
        
        # ML integration configuration
        self.integration_config = {
            'ml_weight': 0.3,  # Weight of ML predictions in final signal
            'rule_based_weight': 0.7,  # Weight of rule-based signals
            'min_ml_confidence': 0.7,  # Minimum ML confidence for integration
            'ml_model_timeout': 5,  # ML prediction timeout in seconds
            'fallback_to_rules': True  # Fallback to rule-based if ML fails
        }
        
        # Signal enhancement configuration
        self.enhancement_config = {
            'enhance_entry_points': True,  # Enhance entry points with ML
            'enhance_patterns': True,  # Enhance patterns with ML
            'enhance_confidence': True,  # Enhance confidence scores with ML
            'ml_pattern_recognition': True  # Use ML for pattern recognition
        }
    
    def generate_ml_enhanced_signals(self, symbol: Symbol) -> List[TradingSignal]:
        """
        Generate signals enhanced with ML predictions
        
        Args:
            symbol: Trading symbol to generate signals for
            
        Returns:
            List of ML-enhanced trading signals
        """
        try:
            logger.info(f"Generating ML-enhanced signals for {symbol.symbol}")
            
            # Get active ML models
            active_models = ChartMLModel.objects.filter(
                is_active=True,
                status='TRAINED',
                target_task='ENTRY_POINT_DETECTION'
            ).order_by('-accuracy_score')
            
            if not active_models.exists():
                logger.warning(f"No active ML models found for {symbol.symbol}")
                if self.integration_config['fallback_to_rules']:
                    return self.signal_service.generate_signals_for_symbol(symbol)
                else:
                    return []
            
            # Generate rule-based signals
            rule_based_signals = self.signal_service.generate_signals_for_symbol(symbol)
            
            # Generate ML-enhanced signals
            ml_enhanced_signals = []
            
            for signal in rule_based_signals:
                try:
                    # Enhance signal with ML predictions
                    enhanced_signal = self._enhance_signal_with_ml(signal, active_models)
                    
                    if enhanced_signal:
                        ml_enhanced_signals.append(enhanced_signal)
                    else:
                        # Fallback to original signal
                        ml_enhanced_signals.append(signal)
                
                except Exception as e:
                    logger.error(f"Error enhancing signal {signal.id}: {e}")
                    ml_enhanced_signals.append(signal)
            
            # Generate additional ML-only signals
            ml_only_signals = self._generate_ml_only_signals(symbol, active_models)
            ml_enhanced_signals.extend(ml_only_signals)
            
            # Filter and rank signals
            filtered_signals = self._filter_and_rank_signals(ml_enhanced_signals)
            
            logger.info(f"Generated {len(filtered_signals)} ML-enhanced signals for {symbol.symbol}")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error generating ML-enhanced signals for {symbol.symbol}: {e}")
            if self.integration_config['fallback_to_rules']:
                return self.signal_service.generate_signals_for_symbol(symbol)
            else:
                return []
    
    def enhance_entry_points_with_ml(self, entry_points: List[EntryPoint]) -> List[EntryPoint]:
        """
        Enhance entry points with ML predictions
        
        Args:
            entry_points: List of entry points to enhance
            
        Returns:
            List of ML-enhanced entry points
        """
        try:
            logger.info(f"Enhancing {len(entry_points)} entry points with ML")
            
            # Get active ML models
            active_models = ChartMLModel.objects.filter(
                is_active=True,
                status='TRAINED',
                target_task='ENTRY_POINT_DETECTION'
            ).order_by('-accuracy_score')
            
            if not active_models.exists():
                logger.warning("No active ML models found for entry point enhancement")
                return entry_points
            
            enhanced_entries = []
            
            for entry_point in entry_points:
                try:
                    # Enhance entry point with ML
                    enhanced_entry = self._enhance_entry_point_with_ml(entry_point, active_models)
                    
                    if enhanced_entry:
                        enhanced_entries.append(enhanced_entry)
                    else:
                        enhanced_entries.append(entry_point)
                
                except Exception as e:
                    logger.error(f"Error enhancing entry point {entry_point.id}: {e}")
                    enhanced_entries.append(entry_point)
            
            logger.info(f"Enhanced {len(enhanced_entries)} entry points with ML")
            return enhanced_entries
            
        except Exception as e:
            logger.error(f"Error enhancing entry points with ML: {e}")
            return entry_points
    
    def enhance_patterns_with_ml(self, patterns: List[ChartPattern]) -> List[ChartPattern]:
        """
        Enhance patterns with ML predictions
        
        Args:
            patterns: List of patterns to enhance
            
        Returns:
            List of ML-enhanced patterns
        """
        try:
            logger.info(f"Enhancing {len(patterns)} patterns with ML")
            
            # Get active ML models for pattern recognition
            pattern_models = ChartMLModel.objects.filter(
                is_active=True,
                status='TRAINED',
                target_task='PATTERN_RECOGNITION'
            ).order_by('-accuracy_score')
            
            if not pattern_models.exists():
                logger.warning("No active ML models found for pattern enhancement")
                return patterns
            
            enhanced_patterns = []
            
            for pattern in patterns:
                try:
                    # Enhance pattern with ML
                    enhanced_pattern = self._enhance_pattern_with_ml(pattern, pattern_models)
                    
                    if enhanced_pattern:
                        enhanced_patterns.append(enhanced_pattern)
                    else:
                        enhanced_patterns.append(pattern)
                
                except Exception as e:
                    logger.error(f"Error enhancing pattern {pattern.id}: {e}")
                    enhanced_patterns.append(pattern)
            
            logger.info(f"Enhanced {len(enhanced_patterns)} patterns with ML")
            return enhanced_patterns
            
        except Exception as e:
            logger.error(f"Error enhancing patterns with ML: {e}")
            return patterns
    
    def predict_with_ml_ensemble(self, chart_image: ChartImage) -> Dict[str, Any]:
        """
        Predict using ML ensemble of multiple models
        
        Args:
            chart_image: Chart image to predict on
            
        Returns:
            Dictionary with ensemble predictions
        """
        try:
            logger.info(f"Making ensemble prediction for chart {chart_image.id}")
            
            # Get active ML models
            active_models = ChartMLModel.objects.filter(
                is_active=True,
                status='TRAINED'
            ).order_by('-accuracy_score')
            
            if not active_models.exists():
                return {'status': 'error', 'message': 'No active ML models found'}
            
            # Get predictions from all models
            predictions = []
            model_weights = []
            
            for model in active_models:
                try:
                    # Make prediction with this model
                    prediction = self._predict_with_single_model(chart_image, model)
                    
                    if prediction['status'] == 'success':
                        predictions.append(prediction)
                        model_weights.append(model.accuracy_score)
                
                except Exception as e:
                    logger.error(f"Error predicting with model {model.id}: {e}")
            
            if not predictions:
                return {'status': 'error', 'message': 'No successful predictions'}
            
            # Combine predictions using weighted average
            ensemble_prediction = self._combine_predictions(predictions, model_weights)
            
            logger.info(f"Ensemble prediction completed with {len(predictions)} models")
            return ensemble_prediction
            
        except Exception as e:
            logger.error(f"Error making ensemble prediction: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _enhance_signal_with_ml(self, signal: TradingSignal, models: List[ChartMLModel]) -> Optional[TradingSignal]:
        """Enhance a signal with ML predictions"""
        try:
            # Get chart image for this signal
            chart_image = self._get_chart_image_for_signal(signal)
            if not chart_image:
                return None
            
            # Get ML predictions
            ml_predictions = []
            for model in models:
                try:
                    prediction = self._predict_with_single_model(chart_image, model)
                    if prediction['status'] == 'success':
                        ml_predictions.append(prediction)
                except Exception as e:
                    logger.error(f"Error predicting with model {model.id}: {e}")
            
            if not ml_predictions:
                return None
            
            # Combine ML predictions
            combined_prediction = self._combine_predictions(ml_predictions, [m.accuracy_score for m in models])
            
            # Enhance signal with ML prediction
            enhanced_signal = self._apply_ml_enhancement(signal, combined_prediction)
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Error enhancing signal with ML: {e}")
            return None
    
    def _enhance_entry_point_with_ml(self, entry_point: EntryPoint, models: List[ChartMLModel]) -> Optional[EntryPoint]:
        """Enhance an entry point with ML predictions"""
        try:
            if not entry_point.chart_image:
                return None
            
            # Get ML predictions
            ml_predictions = []
            for model in models:
                try:
                    prediction = self._predict_with_single_model(entry_point.chart_image, model)
                    if prediction['status'] == 'success':
                        ml_predictions.append(prediction)
                except Exception as e:
                    logger.error(f"Error predicting with model {model.id}: {e}")
            
            if not ml_predictions:
                return None
            
            # Combine ML predictions
            combined_prediction = self._combine_predictions(ml_predictions, [m.accuracy_score for m in models])
            
            # Enhance entry point
            if combined_prediction['confidence'] >= self.integration_config['min_ml_confidence']:
                # Update confidence score with ML enhancement
                ml_weight = self.integration_config['ml_weight']
                rule_weight = self.integration_config['rule_based_weight']
                
                enhanced_confidence = (
                    entry_point.confidence_score * rule_weight +
                    combined_prediction['confidence'] * ml_weight
                )
                
                entry_point.confidence_score = min(0.95, enhanced_confidence)
                
                # Update confidence level
                if enhanced_confidence >= 0.9:
                    entry_point.confidence_level = 'VERY_HIGH'
                elif enhanced_confidence >= 0.8:
                    entry_point.confidence_level = 'HIGH'
                elif enhanced_confidence >= 0.7:
                    entry_point.confidence_level = 'MEDIUM'
                else:
                    entry_point.confidence_level = 'LOW'
            
            return entry_point
            
        except Exception as e:
            logger.error(f"Error enhancing entry point with ML: {e}")
            return None
    
    def _enhance_pattern_with_ml(self, pattern: ChartPattern, models: List[ChartMLModel]) -> Optional[ChartPattern]:
        """Enhance a pattern with ML predictions"""
        try:
            # Get ML predictions for pattern recognition
            ml_predictions = []
            for model in models:
                try:
                    prediction = self._predict_with_single_model(pattern.chart_image, model)
                    if prediction['status'] == 'success':
                        ml_predictions.append(prediction)
                except Exception as e:
                    logger.error(f"Error predicting with model {model.id}: {e}")
            
            if not ml_predictions:
                return None
            
            # Combine ML predictions
            combined_prediction = self._combine_predictions(ml_predictions, [m.accuracy_score for m in models])
            
            # Enhance pattern confidence
            if combined_prediction['confidence'] >= self.integration_config['min_ml_confidence']:
                ml_weight = self.integration_config['ml_weight']
                rule_weight = self.integration_config['rule_based_weight']
                
                enhanced_confidence = (
                    pattern.confidence_score * rule_weight +
                    combined_prediction['confidence'] * ml_weight
                )
                
                pattern.confidence_score = min(0.95, enhanced_confidence)
                
                # Update strength
                if enhanced_confidence >= 0.9:
                    pattern.strength = 'VERY_STRONG'
                elif enhanced_confidence >= 0.8:
                    pattern.strength = 'STRONG'
                elif enhanced_confidence >= 0.7:
                    pattern.strength = 'MODERATE'
                else:
                    pattern.strength = 'WEAK'
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error enhancing pattern with ML: {e}")
            return None
    
    def _generate_ml_only_signals(self, symbol: Symbol, models: List[ChartMLModel]) -> List[TradingSignal]:
        """Generate signals using only ML predictions"""
        try:
            ml_signals = []
            
            # Get recent chart images for this symbol
            recent_charts = ChartImage.objects.filter(
                symbol=symbol,
                is_training_data=True
            ).order_by('-created_at')[:10]
            
            for chart_image in recent_charts:
                try:
                    # Get ML predictions
                    prediction = self.predict_with_ml_ensemble(chart_image)
                    
                    if prediction['status'] == 'success' and prediction['confidence'] >= self.integration_config['min_ml_confidence']:
                        # Create ML-based signal
                        ml_signal = self._create_ml_signal(symbol, chart_image, prediction)
                        
                        if ml_signal:
                            ml_signals.append(ml_signal)
                
                except Exception as e:
                    logger.error(f"Error generating ML signal for chart {chart_image.id}: {e}")
            
            return ml_signals
            
        except Exception as e:
            logger.error(f"Error generating ML-only signals: {e}")
            return []
    
    def _predict_with_single_model(self, chart_image: ChartImage, model: ChartMLModel) -> Dict[str, Any]:
        """Make prediction with a single ML model"""
        try:
            # Import ML training service
            from apps.signals.ml_model_training_service import MLModelTrainingService
            
            ml_service = MLModelTrainingService()
            prediction = ml_service.predict_entry_points(chart_image, model.id)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting with model {model.id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _combine_predictions(self, predictions: List[Dict], weights: List[float]) -> Dict[str, Any]:
        """Combine multiple predictions using weighted average"""
        try:
            if not predictions:
                return {'status': 'error', 'message': 'No predictions to combine'}
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight == 0:
                weights = [1.0] * len(predictions)
                total_weight = len(predictions)
            
            normalized_weights = [w / total_weight for w in weights]
            
            # Combine predictions
            combined_confidence = sum(
                p['confidence'] * w for p, w in zip(predictions, normalized_weights)
            )
            
            # Determine most common prediction
            entry_types = [p['entry_type'] for p in predictions]
            most_common_type = max(set(entry_types), key=entry_types.count)
            
            return {
                'status': 'success',
                'entry_type': most_common_type,
                'confidence': combined_confidence,
                'num_models': len(predictions),
                'individual_predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Error combining predictions: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _apply_ml_enhancement(self, signal: TradingSignal, ml_prediction: Dict[str, Any]) -> TradingSignal:
        """Apply ML enhancement to a signal"""
        try:
            # Enhance confidence score
            ml_weight = self.integration_config['ml_weight']
            rule_weight = self.integration_config['rule_based_weight']
            
            enhanced_confidence = (
                signal.confidence_score * rule_weight +
                ml_prediction['confidence'] * ml_weight
            )
            
            signal.confidence_score = min(0.95, enhanced_confidence)
            
            # Update signal strength
            if enhanced_confidence >= 0.9:
                signal.strength = 'VERY_STRONG'
            elif enhanced_confidence >= 0.8:
                signal.strength = 'STRONG'
            elif enhanced_confidence >= 0.7:
                signal.strength = 'MODERATE'
            else:
                signal.strength = 'WEAK'
            
            # Add ML metadata
            if not signal.metadata:
                signal.metadata = {}
            
            signal.metadata['ml_enhanced'] = True
            signal.metadata['ml_confidence'] = ml_prediction['confidence']
            signal.metadata['ml_entry_type'] = ml_prediction['entry_type']
            signal.metadata['ml_models_used'] = ml_prediction['num_models']
            
            return signal
            
        except Exception as e:
            logger.error(f"Error applying ML enhancement: {e}")
            return signal
    
    def _create_ml_signal(self, symbol: Symbol, chart_image: ChartImage, prediction: Dict[str, Any]) -> Optional[TradingSignal]:
        """Create a signal based on ML prediction"""
        try:
            # Map ML entry type to signal type
            entry_type = prediction['entry_type']
            if entry_type == 'BUY':
                signal_type = 'BUY'
            elif entry_type == 'SELL':
                signal_type = 'SELL'
            else:
                return None  # Skip HOLD signals
            
            # Create signal
            signal = TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence_score=prediction['confidence'],
                strength='STRONG' if prediction['confidence'] >= 0.8 else 'MODERATE',
                entry_price=Decimal(str(chart_image.price_range_high if signal_type == 'BUY' else chart_image.price_range_low)),
                stop_loss=None,  # Will be calculated later
                take_profit=None,  # Will be calculated later
                risk_reward_ratio=1.5,  # Default
                timeframe=chart_image.timeframe,
                metadata={
                    'ml_generated': True,
                    'chart_image_id': chart_image.id,
                    'ml_prediction': prediction
                }
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating ML signal: {e}")
            return None
    
    def _get_chart_image_for_signal(self, signal: TradingSignal) -> Optional[ChartImage]:
        """Get chart image for a signal"""
        try:
            # Try to find chart image from metadata
            if signal.metadata and 'chart_image_id' in signal.metadata:
                try:
                    return ChartImage.objects.get(id=signal.metadata['chart_image_id'])
                except ChartImage.DoesNotExist:
                    pass
            
            # Find recent chart image for this symbol and timeframe
            recent_chart = ChartImage.objects.filter(
                symbol=signal.symbol,
                timeframe=signal.timeframe,
                is_training_data=True
            ).order_by('-created_at').first()
            
            return recent_chart
            
        except Exception as e:
            logger.error(f"Error getting chart image for signal: {e}")
            return None
    
    def _filter_and_rank_signals(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """Filter and rank signals by quality"""
        try:
            # Filter signals by minimum confidence
            filtered_signals = [
                s for s in signals 
                if s.confidence_score >= 0.6
            ]
            
            # Sort by confidence score
            ranked_signals = sorted(filtered_signals, key=lambda x: x.confidence_score, reverse=True)
            
            # Return top signals
            return ranked_signals[:10]  # Top 10 signals
            
        except Exception as e:
            logger.error(f"Error filtering and ranking signals: {e}")
            return signals

