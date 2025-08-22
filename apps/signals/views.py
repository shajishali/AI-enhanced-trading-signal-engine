import logging
from datetime import datetime, timedelta
from typing import Dict, List
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count, Prefetch
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import json
from django.conf import settings

from apps.signals.models import (
    TradingSignal, SignalType, SignalFactor, SignalAlert,
    MarketRegime, SignalPerformance
)
from apps.signals.services import (
    SignalGenerationService, MarketRegimeService, SignalPerformanceService
)
from apps.trading.models import Symbol

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SignalAPIView(View):
    """API view for signal operations"""
    
    def get(self, request):
        """Get signals with optional filtering"""
        try:
            # Get query parameters
            symbol = request.GET.get('symbol')
            signal_type = request.GET.get('signal_type')
            is_valid = request.GET.get('is_valid', 'true').lower() == 'true'
            limit = int(request.GET.get('limit', 50))
            
            # Create cache key based on parameters
            cache_key = f"signals_api_{symbol}_{signal_type}_{is_valid}_{limit}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Returning cached data for key: {cache_key}")
                return JsonResponse(cached_data)
            
            # Build optimized query with select_related and prefetch_related
            queryset = TradingSignal.objects.select_related(
                'symbol', 'signal_type'
            )
            
            if symbol:
                queryset = queryset.filter(symbol__symbol__iexact=symbol)
            
            if signal_type:
                queryset = queryset.filter(signal_type__name=signal_type)
            
            queryset = queryset.filter(is_valid=is_valid)
            signals = queryset.order_by('-created_at')[:limit]
            
            # Get synchronized prices for all symbols
            from apps.signals.price_sync_service import price_sync_service
            
            # Serialize signals with optimized data access and synchronized prices
            signal_data = []
            for signal in signals:
                symbol = signal.symbol.symbol
                
                # Get synchronized price data for this symbol
                sync_prices = price_sync_service.get_synchronized_prices(symbol)
                
                current_price = sync_prices.get('current_price')
                price_change_24h = sync_prices.get('price_change_24h')
                price_discrepancy = sync_prices.get('price_discrepancy_percent', 0)
                price_status = sync_prices.get('price_status', 'unknown')
                price_alert = sync_prices.get('price_alert')
                
                signal_data.append({
                    'id': signal.id,
                    'symbol': symbol,
                    'signal_type': signal.signal_type.name,
                    'strength': signal.strength,
                    'confidence_score': signal.confidence_score,
                    'confidence_level': signal.confidence_level,
                    'entry_price': float(signal.entry_price) if signal.entry_price else None,
                    'target_price': float(signal.target_price) if signal.target_price else None,
                    'stop_loss': float(signal.stop_loss) if signal.stop_loss else None,
                    'current_price': current_price,  # Synchronized current price
                    'price_change_24h': price_change_24h,  # 24h price change
                    'price_discrepancy_percent': price_discrepancy,  # Price difference from entry
                    'price_status': price_status,  # Price reliability status
                    'price_alert': price_alert,  # Price discrepancy alerts
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'quality_score': signal.quality_score,
                    'is_valid': signal.is_valid,
                    'is_executed': signal.is_executed,
                    'is_profitable': signal.is_profitable,
                    'profit_loss': float(signal.profit_loss) if signal.profit_loss else None,
                    'created_at': signal.created_at.isoformat(),
                    'expires_at': signal.expires_at.isoformat() if signal.expires_at else None,
                    'technical_score': signal.technical_score,
                    'sentiment_score': signal.sentiment_score,
                    'news_score': signal.news_score,
                    'volume_score': signal.volume_score,
                    'pattern_score': signal.pattern_score,
                    # New timeframe and entry point fields
                    'timeframe': signal.timeframe,
                    'entry_point_type': signal.entry_point_type,
                    'entry_point_details': signal.entry_point_details,
                    'entry_zone_low': float(signal.entry_zone_low) if signal.entry_zone_low else None,
                    'entry_zone_high': float(signal.entry_zone_high) if signal.entry_zone_high else None,
                    'entry_confidence': signal.entry_confidence
                })
            
            response_data = {
                'success': True,
                'signals': signal_data,
                'count': len(signal_data),
                'cached_at': timezone.now().isoformat()
            }
            
            # Cache the response for 5 minutes
            cache.set(cache_key, response_data, 300)
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Generate signals for a symbol"""
        try:
            data = json.loads(request.body)
            symbol_name = data.get('symbol')
            
            if not symbol_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Symbol is required'
                }, status=400)
            
            # Get symbol
            try:
                symbol = Symbol.objects.get(symbol__iexact=symbol_name)
            except Symbol.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Symbol {symbol_name} not found'
                }, status=404)
            
            # Generate signals
            signal_service = SignalGenerationService()
            signals = signal_service.generate_signals_for_symbol(symbol)
            
            # Invalidate related caches to ensure data consistency
            cache_keys_to_delete = [
                "signal_statistics",
                f"signals_api_{symbol.symbol}_None_true_50",
                f"signals_api_None_None_true_50"
            ]
            
            for cache_key in cache_keys_to_delete:
                cache.delete(cache_key)
                logger.info(f"Invalidated cache key: {cache_key}")
            
            return JsonResponse({
                'success': True,
                'symbol': symbol.symbol,
                'signals_generated': len(signals),
                'signals': [signal.id for signal in signals]
            })
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SignalDetailView(View):
    """API view for individual signal operations"""
    
    def get(self, request, signal_id):
        """Get signal details"""
        try:
            signal = TradingSignal.objects.select_related(
                'symbol', 'signal_type'
            ).prefetch_related('factor_contributions__factor').get(id=signal_id)
            
            # Get factor contributions
            factor_contributions = []
            for contribution in signal.factor_contributions.all():
                factor_contributions.append({
                    'factor_name': contribution.factor.name,
                    'factor_type': contribution.factor.factor_type,
                    'score': contribution.score,
                    'weight': contribution.weight,
                    'contribution': contribution.contribution
                })
            
            signal_data = {
                'id': signal.id,
                'symbol': signal.symbol.symbol,
                'signal_type': signal.signal_type.name,
                'strength': signal.strength,
                'confidence_score': signal.confidence_score,
                'confidence_level': signal.confidence_level,
                'entry_price': float(signal.entry_price) if signal.entry_price else None,
                'target_price': float(signal.target_price) if signal.target_price else None,
                'stop_loss': float(signal.stop_loss) if signal.stop_loss else None,
                'risk_reward_ratio': signal.risk_reward_ratio,
                'quality_score': signal.quality_score,
                'is_valid': signal.is_valid,
                'is_executed': signal.is_executed,
                'is_profitable': signal.is_profitable,
                'profit_loss': float(signal.profit_loss) if signal.profit_loss else None,
                'created_at': signal.created_at.isoformat(),
                'expires_at': signal.expires_at.isoformat() if signal.expires_at else None,
                'technical_score': signal.technical_score,
                'sentiment_score': signal.sentiment_score,
                'news_score': signal.news_score,
                'volume_score': signal.volume_score,
                'pattern_score': signal.pattern_score,
                'factor_contributions': factor_contributions
            }
            
            return JsonResponse({
                'success': True,
                'signal': signal_data
            })
            
        except TradingSignal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Signal not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error getting signal {signal_id}: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def put(self, request, signal_id):
        """Update signal (e.g., mark as executed)"""
        try:
            data = json.loads(request.body)
            signal = TradingSignal.objects.get(id=signal_id)
            
            # Update fields
            if 'is_executed' in data:
                signal.is_executed = data['is_executed']
                if data['is_executed']:
                    signal.executed_at = timezone.now()
            
            if 'execution_price' in data:
                signal.execution_price = data['execution_price']
            
            if 'is_profitable' in data:
                signal.is_profitable = data['is_profitable']
            
            if 'profit_loss' in data:
                signal.profit_loss = data['profit_loss']
            
            signal.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Signal updated successfully'
            })
            
        except TradingSignal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Signal not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error updating signal {signal_id}: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SignalPerformanceView(View):
    """API view for signal performance metrics"""
    
    def get(self, request):
        """Get performance metrics"""
        try:
            # Get query parameters
            period_type = request.GET.get('period_type', '1D')
            
            # Calculate performance metrics
            performance_service = SignalPerformanceService()
            metrics = performance_service.calculate_performance_metrics(period_type)
            
            # Get recent performance records
            recent_performance = SignalPerformance.objects.filter(
                period_type=period_type
            ).order_by('-created_at')[:10]
            
            performance_history = []
            for record in recent_performance:
                performance_history.append({
                    'period_type': record.period_type,
                    'start_date': record.start_date.isoformat(),
                    'end_date': record.end_date.isoformat(),
                    'total_signals': record.total_signals,
                    'profitable_signals': record.profitable_signals,
                    'win_rate': record.win_rate,
                    'profit_factor': record.profit_factor,
                    'average_confidence': record.average_confidence,
                    'average_quality': record.average_quality_score
                })
            
            return JsonResponse({
                'success': True,
                'current_metrics': metrics,
                'performance_history': performance_history
            })
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MarketRegimeView(View):
    """API view for market regime detection"""
    
    def get(self, request):
        """Get market regimes"""
        try:
            symbol = request.GET.get('symbol')
            
            if symbol:
                # Get regime for specific symbol
                try:
                    symbol_obj = Symbol.objects.get(symbol__iexact=symbol)
                    regime_service = MarketRegimeService()
                    regime = regime_service.detect_market_regime(symbol_obj)
                    
                    if regime:
                        regime_data = {
                            'name': regime.name,
                            'description': regime.description,
                            'volatility_level': regime.volatility_level,
                            'trend_strength': regime.trend_strength,
                            'confidence': regime.confidence,
                            'created_at': regime.created_at.isoformat()
                        }
                    else:
                        regime_data = None
                    
                    return JsonResponse({
                        'success': True,
                        'symbol': symbol,
                        'regime': regime_data
                    })
                    
                except Symbol.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'Symbol {symbol} not found'
                    }, status=404)
            else:
                # Get all recent regimes
                recent_regimes = MarketRegime.objects.order_by('-created_at')[:20]
                
                regime_data = []
                for regime in recent_regimes:
                    regime_data.append({
                        'name': regime.name,
                        'description': regime.description,
                        'volatility_level': regime.volatility_level,
                        'trend_strength': regime.trend_strength,
                        'confidence': regime.confidence,
                        'created_at': regime.created_at.isoformat()
                    })
                
                return JsonResponse({
                    'success': True,
                    'regimes': regime_data
                })
            
        except Exception as e:
            logger.error(f"Error getting market regimes: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Detect market regimes for all symbols"""
        try:
            regime_service = MarketRegimeService()
            active_symbols = Symbol.objects.filter(is_active=True)
            
            regimes_detected = 0
            for symbol in active_symbols:
                try:
                    regime = regime_service.detect_market_regime(symbol)
                    if regime:
                        regimes_detected += 1
                except Exception as e:
                    logger.error(f"Error detecting regime for {symbol.symbol}: {e}")
            
            return JsonResponse({
                'success': True,
                'regimes_detected': regimes_detected,
                'symbols_processed': active_symbols.count()
            })
            
        except Exception as e:
            logger.error(f"Error detecting market regimes: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SignalAlertView(View):
    """API view for signal alerts"""
    
    def get(self, request):
        """Get alerts"""
        try:
            # Get query parameters
            alert_type = request.GET.get('alert_type')
            priority = request.GET.get('priority')
            is_read = request.GET.get('is_read')
            limit = int(request.GET.get('limit', 50))
            
            # Build query
            queryset = SignalAlert.objects.select_related('signal__symbol')
            
            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)
            
            if priority:
                queryset = queryset.filter(priority=priority)
            
            if is_read is not None:
                is_read_bool = is_read.lower() == 'true'
                queryset = queryset.filter(is_read=is_read_bool)
            
            alerts = queryset.order_by('-created_at')[:limit]
            
            # Serialize alerts
            alert_data = []
            for alert in alerts:
                alert_data.append({
                    'id': alert.id,
                    'alert_type': alert.alert_type,
                    'priority': alert.priority,
                    'title': alert.title,
                    'message': alert.message,
                    'signal_id': alert.signal.id if alert.signal else None,
                    'signal_symbol': alert.signal.symbol.symbol if alert.signal else None,
                    'is_read': alert.is_read,
                    'created_at': alert.created_at.isoformat()
                })
            
            return JsonResponse({
                'success': True,
                'alerts': alert_data,
                'count': len(alert_data)
            })
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Mark alerts as read"""
        try:
            data = json.loads(request.body)
            alert_ids = data.get('alert_ids', [])
            
            if not alert_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Alert IDs are required'
                }, status=400)
            
            # Mark alerts as read
            updated = SignalAlert.objects.filter(id__in=alert_ids).update(is_read=True)
            
            return JsonResponse({
                'success': True,
                'alerts_marked_read': updated
            })
            
        except Exception as e:
            logger.error(f"Error marking alerts as read: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@login_required
def signal_dashboard(request):
    """Signal dashboard view"""
    try:
        # Get recent signals
        recent_signals = TradingSignal.objects.select_related(
            'symbol', 'signal_type'
        ).filter(is_valid=True).order_by('-created_at')[:10]
        
        # Get performance metrics
        performance_service = SignalPerformanceService()
        daily_metrics = performance_service.calculate_performance_metrics('1D')
        
        # Get active alerts
        active_alerts = SignalAlert.objects.filter(is_read=False).order_by('-created_at')[:5]
        
        # Get market regimes
        recent_regimes = MarketRegime.objects.order_by('-created_at')[:5]
        
        # Calculate statistics
        total_signals = TradingSignal.objects.count()
        active_signals = TradingSignal.objects.filter(is_valid=True).count()
        executed_signals = TradingSignal.objects.filter(is_executed=True).count()
        profitable_signals = TradingSignal.objects.filter(
            is_executed=True, is_profitable=True
        ).count()
        
        win_rate = profitable_signals / executed_signals if executed_signals > 0 else 0.0
        
        context = {
            'recent_signals': recent_signals,
            'daily_metrics': daily_metrics,
            'active_alerts': active_alerts,
            'recent_regimes': recent_regimes,
            'total_signals': total_signals,
            'active_signals': active_signals,
            'executed_signals': executed_signals,
            'profitable_signals': profitable_signals,
            'win_rate': win_rate
        }
        
        return render(request, 'signals/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error rendering signal dashboard: {e}")
        return render(request, 'signals/dashboard.html', {'error': str(e)})


@require_http_methods(["GET"])
def signal_statistics(request):
    """Get signal statistics"""
    try:
        # Check cache first
        cache_key = "signal_statistics"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            logger.info("Returning cached signal statistics")
            return JsonResponse(cached_stats)
        
        # Calculate statistics with optimized queries
        total_signals = TradingSignal.objects.count()
        active_signals = TradingSignal.objects.filter(is_valid=True).count()
        executed_signals = TradingSignal.objects.filter(is_executed=True).count()
        profitable_signals = TradingSignal.objects.filter(
            is_executed=True, is_profitable=True
        ).count()
        
        win_rate = profitable_signals / executed_signals if executed_signals > 0 else 0.0
        
        # Get average metrics for recent signals with optimized query
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).aggregate(
            avg_confidence=Avg('confidence_score'),
            avg_quality=Avg('quality_score')
        )
        
        avg_confidence = recent_signals['avg_confidence'] or 0.0
        avg_quality = recent_signals['avg_quality'] or 0.0
        
        # Get signal distribution by type with optimized query
        signal_distribution = TradingSignal.objects.values('signal_type__name').annotate(
            count=Count('id')
        )
        
        # Get signal distribution by strength with optimized query
        strength_distribution = TradingSignal.objects.values('strength').annotate(
            count=Count('id')
        )
        
        statistics = {
            'total_signals': total_signals,
            'active_signals': active_signals,
            'executed_signals': executed_signals,
            'profitable_signals': profitable_signals,
            'win_rate': win_rate,
            'avg_confidence': avg_confidence,
            'avg_quality': avg_quality,
            'signal_distribution': list(signal_distribution),
            'strength_distribution': list(strength_distribution),
            'cached_at': timezone.now().isoformat()
        }
        
        response_data = {
            'success': True,
            'statistics': statistics
        }
        
        # Cache the statistics for 10 minutes
        cache.set(cache_key, response_data, 600)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting signal statistics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def execute_signal(request, signal_id):
    """Execute a trading signal"""
    try:
        # Get the signal
        try:
            signal = TradingSignal.objects.get(id=signal_id)
        except TradingSignal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Signal {signal_id} not found'
            }, status=404)
        
        # Check if signal is valid and not already executed
        if not signal.is_valid:
            return JsonResponse({
                'success': False,
                'error': 'Signal is not valid'
            }, status=400)
        
        if signal.is_executed:
            return JsonResponse({
                'success': False,
                'error': 'Signal has already been executed'
            }, status=400)
        
        # Check if signal has expired
        if signal.expires_at and signal.expires_at < timezone.now():
            return JsonResponse({
                'success': False,
                'error': 'Signal has expired'
            }, status=400)
        
        # Execute the signal
        signal.is_executed = True
        signal.executed_at = timezone.now()
        signal.save()
        
        # Invalidate related caches to ensure data consistency
        cache_keys_to_delete = [
            "signal_statistics",
            f"signals_api_{signal.symbol.symbol}_None_true_50",
            f"signals_api_None_None_true_50"
        ]
        
        for cache_key in cache_keys_to_delete:
            cache.delete(cache_key)
            logger.info(f"Invalidated cache key: {cache_key}")
        
        # Log the execution
        logger.info(f"Signal {signal_id} executed successfully for {signal.symbol.symbol}")
        
        return JsonResponse({
            'success': True,
            'message': f'Signal {signal_id} executed successfully',
            'signal': {
                'id': signal.id,
                'symbol': signal.symbol.symbol,
                'signal_type': signal.signal_type.name,
                'executed_at': signal.executed_at.isoformat(),
                'entry_price': float(signal.entry_price) if signal.entry_price else None,
                'target_price': float(signal.target_price) if signal.target_price else None,
                'stop_loss': float(signal.stop_loss) if signal.stop_loss else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error executing signal {signal_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def generate_signals_manual(request):
    """Manually trigger signal generation"""
    try:
        data = json.loads(request.body)
        symbol_name = data.get('symbol')
        
        if not symbol_name:
            return JsonResponse({
                'success': False,
                'error': 'Symbol is required'
            }, status=400)
        
        # Get symbol
        try:
            symbol = Symbol.objects.get(symbol__iexact=symbol_name)
        except Symbol.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Symbol {symbol_name} not found'
            }, status=404)
        
        # Generate signals
        signal_service = SignalGenerationService()
        signals = signal_service.generate_signals_for_symbol(symbol)
        
        # Invalidate related caches to ensure data consistency
        cache_keys_to_delete = [
            "signal_statistics",
            f"signals_api_{symbol.symbol}_None_true_50",
            f"signals_api_None_None_true_50"
        ]
        
        for cache_key in cache_keys_to_delete:
            cache.delete(cache_key)
            logger.info(f"Invalidated cache key: {cache_key}")
        
        return JsonResponse({
            'success': True,
            'symbol': symbol.symbol,
            'signals_generated': len(signals),
            'signals': [signal.id for signal in signals]
        })
        
    except Exception as e:
        logger.error(f"Error generating signals manually: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
def reset_signals_for_testing(request):
    """Reset all signals to 'Active' status for testing purposes"""
    try:
        # Only allow in development/testing environment
        if not settings.DEBUG:
            return JsonResponse({
                'success': False,
                'error': 'This endpoint is only available in development mode'
            }, status=403)
        
        # Reset all signals to not executed
        signals_updated = TradingSignal.objects.filter(is_executed=True).update(
            is_executed=False,
            executed_at=None
        )
        
        # Clear related caches
        cache_keys_to_delete = [
            "signal_statistics",
            "signals_api_None_None_true_50"
        ]
        
        for cache_key in cache_keys_to_delete:
            cache.delete(cache_key)
            logger.info(f"Invalidated cache key: {cache_key}")
        
        logger.info(f"Reset {signals_updated} signals for testing")
        
        return JsonResponse({
            'success': True,
            'message': f'Reset {signals_updated} signals for testing',
            'signals_reset': signals_updated
        })
        
    except Exception as e:
        logger.error(f"Error resetting signals for testing: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def sync_signal_prices(request):
    """Synchronize prices for all active signals"""
    try:
        from apps.signals.price_sync_service import price_sync_service
        
        # Get all active signals
        active_signals = TradingSignal.objects.filter(
            is_valid=True,
            is_executed=False
        )
        
        synced_count = 0
        errors = []
        
        for signal in active_signals:
            try:
                # Update signal prices using the sync service
                if price_sync_service.update_signal_prices(signal.id):
                    synced_count += 1
            except Exception as e:
                errors.append(f"Error syncing {signal.symbol.symbol}: {str(e)}")
                logger.warning(f"Error syncing signal {signal.id}: {e}")
        
        # Clear signal caches to force refresh
        cache_keys_to_delete = [
            "signal_statistics",
            "signals_api_None_None_true_50"
        ]
        
        for cache_key in cache_keys_to_delete:
            cache.delete(cache_key)
        
        logger.info(f"Successfully synchronized prices for {synced_count} signals")
        
        response_data = {
            'success': True,
            'synced_count': synced_count,
            'total_signals': len(active_signals),
            'message': f'Successfully synchronized prices for {synced_count}/{len(active_signals)} signals'
        }
        
        if errors:
            response_data['warnings'] = errors
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error synchronizing signal prices: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
