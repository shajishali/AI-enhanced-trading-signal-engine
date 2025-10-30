"""
Database-driven signal generation tasks
Updated Celery tasks that use database data instead of live APIs
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from celery import shared_task
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.cache import cache

from apps.signals.models import (
    TradingSignal, SignalType, SignalAlert, SignalPerformance,
    MarketRegime, SignalStrength
)
from apps.signals.database_signal_service import database_signal_service
from apps.signals.database_technical_analysis import database_technical_analysis
from apps.signals.database_data_utils import (
    get_database_health_status, validate_data_quality,
    get_symbols_with_recent_data, get_data_statistics
)
from apps.trading.models import Symbol
from apps.data.models import MarketData

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_database_signals_task(self):
    """Generate signals using database data instead of live APIs"""
    try:
        logger.info("Starting database-driven signal generation...")
        
        # Check database health first
        health_status = get_database_health_status()
        if health_status['status'] == 'CRITICAL':
            logger.error(f"Database health critical: {health_status['reason']}")
            return {
                'success': False,
                'error': 'Database health critical',
                'health_status': health_status
            }
        
        # Generate signals using database service
        result = database_signal_service.generate_best_signals_for_all_coins()
        
        logger.info(
            f"Database signal generation completed: "
            f"{result['total_signals_generated']} total signals, "
            f"{result['best_signals_selected']} best signals selected, "
            f"{result['processed_symbols']} symbols processed"
        )
        
        # Log best signals
        if result['best_signals']:
            logger.info("Best signals generated:")
            for i, signal in enumerate(result['best_signals'], 1):
                logger.info(
                    f"{i}. {signal['symbol'].symbol} {signal['signal_type']} - "
                    f"Confidence: {signal['confidence_score']:.1%}, "
                    f"Entry: ${signal['entry_price']:.2f}"
                )
        
        return {
            'success': True,
            'total_signals': result['total_signals_generated'],
            'best_signals': result['best_signals_selected'],
            'processed_symbols': result['processed_symbols'],
            'health_status': health_status
        }
        
    except Exception as e:
        logger.error(f"Database signal generation failed: {e}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_database_signals_for_symbol(symbol_id: int):
    """Generate database signals for a specific symbol"""
    try:
        symbol = Symbol.objects.get(id=symbol_id)
        logger.info(f"Generating database signals for {symbol.symbol}")
        
        # Validate data quality
        quality = validate_data_quality(symbol, hours_back=24)
        if not quality['is_valid']:
            logger.warning(f"Insufficient data quality for {symbol.symbol}: {quality['reason']}")
            return {
                'success': False,
                'error': f'Data quality issue: {quality["reason"]}',
                'quality': quality
            }
        
        # Get recent market data
        from apps.signals.database_data_utils import get_recent_market_data
        market_data = get_recent_market_data(symbol, hours_back=24)
        
        # Generate signals
        signals = database_signal_service.generate_logical_signals_for_symbol(symbol, market_data)
        
        logger.info(f"Generated {len(signals)} database signals for {symbol.symbol}")
        
        return {
            'success': True,
            'symbol': symbol.symbol,
            'signals_generated': len(signals),
            'signals': [signal.id for signal in signals],
            'quality': quality
        }
        
    except Symbol.DoesNotExist:
        logger.error(f"Symbol with id {symbol_id} not found")
        return {'success': False, 'error': 'Symbol not found'}
    except Exception as e:
        logger.error(f"Error generating database signals for symbol {symbol_id}: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def validate_database_data_quality_task():
    """Validate database data quality before signal generation"""
    try:
        logger.info("Starting database data quality validation...")
        
        # Get database health status
        health_status = get_database_health_status()
        
        # Get symbols with recent data
        symbols_with_data = get_symbols_with_recent_data(hours_back=24, min_data_points=20)
        
        # Validate each symbol
        validation_results = []
        valid_symbols = 0
        invalid_symbols = 0
        
        for symbol in symbols_with_data:
            quality = validate_data_quality(symbol, hours_back=24)
            validation_results.append({
                'symbol': symbol.symbol,
                'is_valid': quality['is_valid'],
                'data_points': quality['data_points'],
                'completeness': quality.get('completeness', 0),
                'data_age_hours': quality['data_age_hours']
            })
            
            if quality['is_valid']:
                valid_symbols += 1
            else:
                invalid_symbols += 1
        
        # Calculate overall quality metrics
        total_symbols = len(symbols_with_data)
        quality_percentage = (valid_symbols / total_symbols * 100) if total_symbols > 0 else 0
        
        logger.info(
            f"Data quality validation completed: "
            f"{valid_symbols}/{total_symbols} symbols valid ({quality_percentage:.1f}%)"
        )
        
        return {
            'success': True,
            'health_status': health_status,
            'total_symbols': total_symbols,
            'valid_symbols': valid_symbols,
            'invalid_symbols': invalid_symbols,
            'quality_percentage': quality_percentage,
            'validation_results': validation_results
        }
        
    except Exception as e:
        logger.error(f"Error validating database data quality: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def calculate_database_technical_indicators_task():
    """Calculate technical indicators from database data"""
    try:
        logger.info("Starting database technical indicator calculation...")
        
        # Get symbols with recent data
        symbols_with_data = get_symbols_with_recent_data(hours_back=168, min_data_points=50)  # 1 week
        
        indicators_calculated = 0
        errors = 0
        
        for symbol in symbols_with_data:
            try:
                # Calculate indicators
                indicators = database_technical_analysis.calculate_indicators_from_database(
                    symbol, hours_back=168
                )
                
                if indicators:
                    # Save to database
                    success = database_technical_analysis.save_indicators_to_database(symbol, indicators)
                    if success:
                        indicators_calculated += 1
                        logger.info(f"Calculated indicators for {symbol.symbol}")
                    else:
                        errors += 1
                        logger.error(f"Failed to save indicators for {symbol.symbol}")
                else:
                    errors += 1
                    logger.warning(f"No indicators calculated for {symbol.symbol}")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Error calculating indicators for {symbol.symbol}: {e}")
        
        logger.info(
            f"Technical indicator calculation completed: "
            f"{indicators_calculated} successful, {errors} errors"
        )
        
        return {
            'success': True,
            'indicators_calculated': indicators_calculated,
            'errors': errors,
            'total_symbols': len(symbols_with_data)
        }
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def monitor_database_signal_performance():
    """Monitor database signal performance and quality"""
    try:
        logger.info("Starting database signal performance monitoring...")
        
        # Get recent database signals
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24),
            data_source='database'
        )
        
        if not recent_signals.exists():
            logger.info("No recent database signals found")
            return {
                'success': True,
                'signals_analyzed': 0,
                'message': 'No recent database signals found'
            }
        
        # Calculate performance metrics
        total_signals = recent_signals.count()
        avg_confidence = recent_signals.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0
        avg_quality = recent_signals.aggregate(avg_quality=Avg('quality_score'))['avg_quality'] or 0
        
        # Analyze signal distribution
        signal_types = recent_signals.values('signal_type__name').annotate(count=Count('id'))
        signal_strengths = recent_signals.values('strength__name').annotate(count=Count('id'))
        
        # Check for quality issues
        low_confidence_signals = recent_signals.filter(confidence_score__lt=0.5).count()
        low_quality_signals = recent_signals.filter(quality_score__lt=0.6).count()
        
        performance_metrics = {
            'total_signals': total_signals,
            'avg_confidence': avg_confidence,
            'avg_quality': avg_quality,
            'low_confidence_signals': low_confidence_signals,
            'low_quality_signals': low_quality_signals,
            'signal_types': list(signal_types),
            'signal_strengths': list(signal_strengths)
        }
        
        # Create alerts for performance issues
        alerts_created = 0
        if low_confidence_signals > total_signals * 0.3:  # More than 30% low confidence
            SignalAlert.objects.create(
                alert_type='PERFORMANCE_ALERT',
                priority='HIGH',
                title="High Number of Low Confidence Signals",
                message=f"{low_confidence_signals} signals have confidence < 50%"
            )
            alerts_created += 1
        
        if low_quality_signals > total_signals * 0.2:  # More than 20% low quality
            SignalAlert.objects.create(
                alert_type='PERFORMANCE_ALERT',
                priority='MEDIUM',
                title="High Number of Low Quality Signals",
                message=f"{low_quality_signals} signals have quality < 60%"
            )
            alerts_created += 1
        
        logger.info(
            f"Database signal performance monitoring completed: "
            f"{total_signals} signals analyzed, {alerts_created} alerts created"
        )
        
        return {
            'success': True,
            'signals_analyzed': total_signals,
            'performance_metrics': performance_metrics,
            'alerts_created': alerts_created
        }
        
    except Exception as e:
        logger.error(f"Error monitoring database signal performance: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_database_signal_cache():
    """Clean up database signal generation cache"""
    try:
        logger.info("Starting database signal cache cleanup...")
        
        # Clear price cache
        from apps.signals.database_data_utils import clear_price_cache
        clear_price_cache()
        
        # Clear indicators cache
        database_technical_analysis.clear_indicators_cache()
        
        # Clear any other signal-related cache
        cache_keys_to_clear = [
            'signal_statistics',
            'database_health_status',
            'symbols_with_recent_data'
        ]
        
        for key in cache_keys_to_clear:
            cache.delete(key)
        
        logger.info("Database signal cache cleanup completed")
        
        return {
            'success': True,
            'message': 'Cache cleanup completed'
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up database signal cache: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def database_signal_health_check():
    """Health check for database signal generation system"""
    try:
        logger.info("Starting database signal health check...")
        
        # Check database health
        health_status = get_database_health_status()
        
        # Check recent signal generation
        recent_signals = TradingSignal.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1),
            data_source='database'
        ).count()
        
        # Check data quality
        symbols_with_data = get_symbols_with_recent_data(hours_back=24, min_data_points=20)
        data_quality_percentage = len(symbols_with_data) / Symbol.objects.filter(
            is_active=True, is_crypto_symbol=True
        ).count() * 100 if Symbol.objects.filter(is_active=True, is_crypto_symbol=True).exists() else 0
        
        # Check for errors in recent tasks
        from django_celery_results.models import TaskResult
        recent_failed_tasks = TaskResult.objects.filter(
            status='FAILURE',
            date_created__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Calculate health score
        health_score = 100
        issues = []
        
        if health_status['status'] == 'CRITICAL':
            health_score -= 40
            issues.append(f"Database health critical: {health_status['reason']}")
        elif health_status['status'] == 'WARNING':
            health_score -= 20
            issues.append(f"Database health warning: {health_status['reason']}")
        
        if recent_signals == 0:
            health_score -= 30
            issues.append("No database signals generated in the last hour")
        
        if data_quality_percentage < 80:
            health_score -= 20
            issues.append(f"Low data quality: {data_quality_percentage:.1f}%")
        
        if recent_failed_tasks > 5:
            health_score -= 15
            issues.append(f"High number of failed tasks: {recent_failed_tasks}")
        
        health_status_final = 'healthy' if health_score >= 80 else 'warning' if health_score >= 50 else 'critical'
        
        health_metrics = {
            'health_score': health_score,
            'health_status': health_status_final,
            'issues': issues,
            'database_health': health_status,
            'recent_signals': recent_signals,
            'data_quality_percentage': data_quality_percentage,
            'failed_tasks': recent_failed_tasks
        }
        
        logger.info(
            f"Database signal health check completed - "
            f"Score: {health_score}, Status: {health_status_final}"
        )
        
        return health_metrics
        
    except Exception as e:
        logger.error(f"Error during database signal health check: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def generate_hybrid_signals_task():
    """Generate signals using hybrid approach (database + live API fallback)"""
    try:
        logger.info("Starting hybrid signal generation...")
        
        # Check database health
        health_status = get_database_health_status()
        
        if health_status['status'] in ['HEALTHY', 'WARNING']:
            # Use database signals
            logger.info("Using database signals (primary)")
            result = generate_database_signals_task()
            result['signal_source'] = 'database'
        else:
            # Fallback to live API signals
            logger.warning("Database health critical, falling back to live API signals")
            from apps.signals.tasks import generate_signals_for_all_symbols
            result = generate_signals_for_all_symbols()
            result['signal_source'] = 'live_api'
            result['fallback_reason'] = f"Database health: {health_status['status']}"
        
        logger.info(f"Hybrid signal generation completed using {result.get('signal_source', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in hybrid signal generation: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def update_database_signal_statistics():
    """Update statistics for database-driven signals"""
    try:
        logger.info("Starting database signal statistics update...")
        
        # Get database signal statistics
        total_database_signals = TradingSignal.objects.filter(data_source='database').count()
        recent_database_signals = TradingSignal.objects.filter(
            data_source='database',
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        # Calculate metrics
        avg_confidence = recent_database_signals.aggregate(
            avg_confidence=Avg('confidence_score')
        )['avg_confidence'] or 0.0
        
        avg_quality = recent_database_signals.aggregate(
            avg_quality=Avg('quality_score')
        )['avg_quality'] or 0.0
        
        # Signal type distribution
        signal_type_distribution = recent_database_signals.values(
            'signal_type__name'
        ).annotate(count=Count('id'))
        
        # Strength distribution
        strength_distribution = recent_database_signals.values(
            'strength__name'
        ).annotate(count=Count('id'))
        
        statistics = {
            'total_database_signals': total_database_signals,
            'recent_database_signals': recent_database_signals.count(),
            'avg_confidence': avg_confidence,
            'avg_quality': avg_quality,
            'signal_type_distribution': list(signal_type_distribution),
            'strength_distribution': list(strength_distribution)
        }
        
        logger.info(
            f"Database signal statistics updated - "
            f"Total: {total_database_signals}, Recent: {recent_database_signals.count()}"
        )
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error updating database signal statistics: {e}")
        return {'success': False, 'error': str(e)}












