from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import DataSyncLog, Symbol, MarketData, TechnicalIndicator
from .historical_data_manager import HistoricalDataManager
from .services import CryptoDataIngestionService, TechnicalAnalysisService

logger = logging.getLogger(__name__)


@shared_task
def sync_crypto_symbols_task():
    """Celery task to sync crypto symbols"""
    try:
        service = CryptoDataIngestionService()
        success = service.sync_crypto_symbols()
        
        # Log the sync operation
        DataSyncLog.objects.create(
            source=service.data_source,
            sync_type='SYMBOLS',
            status='SUCCESS' if success else 'FAILED',
            start_time=timezone.now() - timedelta(minutes=5),
            end_time=timezone.now(),
            records_processed=Symbol.objects.filter(symbol_type='CRYPTO').count()
        )
        
        return success
    except Exception as e:
        logger.error(f"Error in sync_crypto_symbols_task: {e}")
        
        # Log the failed sync
        DataSyncLog.objects.create(
            source=service.data_source,
            sync_type='SYMBOLS',
            status='FAILED',
            start_time=timezone.now() - timedelta(minutes=5),
            end_time=timezone.now(),
            error_message=str(e)
        )
        
        return False


@shared_task
def sync_market_data_task():
    """Celery task to sync market data for all active crypto symbols"""
    try:
        service = CryptoDataIngestionService()
        symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
        
        success_count = 0
        total_count = len(symbols)
        
        for symbol in symbols:
            try:
                if service.sync_market_data(symbol):
                    success_count += 1
            except Exception as e:
                logger.error(f"Error syncing market data for {symbol.symbol}: {e}")
        
        # Log the sync operation
        DataSyncLog.objects.create(
            source=service.data_source,
            sync_type='MARKET_DATA',
            status='SUCCESS' if success_count > 0 else 'FAILED',
            start_time=timezone.now() - timedelta(minutes=10),
            end_time=timezone.now(),
            records_processed=success_count,
            total_records=total_count
        )
        
        return success_count > 0
    except Exception as e:
        logger.error(f"Error in sync_market_data_task: {e}")
        return False


@shared_task
def calculate_technical_indicators_task():
    """Celery task to calculate technical indicators for all active symbols"""
    try:
        service = TechnicalAnalysisService()
        symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
        
        success_count = 0
        total_count = len(symbols)
        
        for symbol in symbols:
            try:
                if service.calculate_all_indicators(symbol):
                    success_count += 1
            except Exception as e:
                logger.error(f"Error calculating indicators for {symbol.symbol}: {e}")
        
        # Log the sync operation
        DataSyncLog.objects.create(
            source=service.data_source,
            sync_type='TECHNICAL_INDICATORS',
            status='SUCCESS' if success_count > 0 else 'FAILED',
            start_time=timezone.now() - timedelta(minutes=5),
            end_time=timezone.now(),
            records_processed=success_count,
            total_records=total_count
        )
        
        return success_count > 0
    except Exception as e:
        logger.error(f"Error in calculate_technical_indicators_task: {e}")
        return False


@shared_task
def cleanup_old_data_task():
    """Celery task to cleanup old market data and indicators"""
    try:
        # Retention by timeframe
        cutoff_1m = timezone.now() - timedelta(days=365)
        cutoff_1h = timezone.now() - timedelta(days=730)
        cutoff_1d = timezone.now() - timedelta(days=1825)

        old_1m = MarketData.objects.filter(timestamp__lt=cutoff_1m, timeframe='1m')
        old_1h = MarketData.objects.filter(timestamp__lt=cutoff_1h, timeframe='1h')
        old_1d = MarketData.objects.filter(timestamp__lt=cutoff_1d, timeframe='1d')

        market_data_deleted = old_1m.count() + old_1h.count() + old_1d.count()

        old_1m.delete()
        old_1h.delete()
        old_1d.delete()

        # Indicators: keep 2 years
        cutoff_ind = timezone.now() - timedelta(days=730)
        old_indicators = TechnicalIndicator.objects.filter(timestamp__lt=cutoff_ind)
        indicators_deleted = old_indicators.count()
        old_indicators.delete()
        
        logger.info(f"Cleaned up {market_data_deleted} old market data records and {indicators_deleted} old indicators")
        
        return True
    except Exception as e:
        logger.error(f"Error in cleanup_old_data_task: {e}")
        return False


@shared_task
def update_historical_data_task():
    """Daily incremental update for historical data (last 2 days)."""
    try:
        manager = HistoricalDataManager()
        symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)
        success = 0
        for sym in symbols:
            try:
                end = timezone.now()
                start = end - timedelta(days=2)
                if manager.fetch_complete_historical_data(sym, timeframe='1h', start=start, end=end):
                    success += 1
            except Exception as e:
                logger.error(f"Incremental update failed for {sym.symbol}: {e}")
        logger.info(f"Incremental updates completed for {success}/{symbols.count()} symbols")
        return True
    except Exception as e:
        logger.error(f"Error in update_historical_data_task: {e}")
        return False


@shared_task
def weekly_gap_check_and_fill_task():
    """Weekly task: check last 90 days for gaps and fill them."""
    try:
        manager = HistoricalDataManager()
        symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)[:50]
        for sym in symbols:
            report = manager.check_data_quality(sym, timeframe='1h', days_back=90)
            if report.get('has_gaps'):
                manager.fill_data_gaps(sym, timeframe='1h')
        logger.info("Weekly gap check/fill completed")
        return True
    except Exception as e:
        logger.error(f"Error in weekly_gap_check_and_fill_task: {e}")
        return False


@shared_task
def health_check_task():
    """Celery task to perform system health check"""
    try:
        # Check data freshness
        latest_data = MarketData.objects.order_by('-timestamp').first()
        if latest_data:
            data_age = timezone.now() - latest_data.timestamp
            if data_age > timedelta(hours=1):
                logger.warning(f"Market data is {data_age} old")
        
        # Check symbol count
        symbol_count = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True).count()
        if symbol_count < 50:
            logger.warning(f"Only {symbol_count} active crypto symbols found")
        
        # Check recent sync logs
        recent_syncs = DataSyncLog.objects.filter(
            end_time__gte=timezone.now() - timedelta(hours=1)
        )
        
        failed_syncs = recent_syncs.filter(status='FAILED')
        if failed_syncs.exists():
            logger.warning(f"Found {failed_syncs.count()} failed syncs in the last hour")
        
        return True
    except Exception as e:
        logger.error(f"Error in health_check_task: {e}")
        return False




