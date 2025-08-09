from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

from .models import MarketData, TechnicalIndicator, Symbol, DataSyncLog
from .services import CryptoDataIngestionService, TechnicalAnalysisService

logger = logging.getLogger(__name__)


@csrf_exempt
def get_market_data(request, symbol_id):
    """Get market data for a symbol"""
    try:
        symbol = Symbol.objects.get(id=symbol_id)
        market_data = MarketData.objects.filter(symbol=symbol).order_by('-timestamp')[:100]
        
        data = []
        for md in market_data:
            data.append({
                'timestamp': md.timestamp.isoformat(),
                'open': float(md.open_price),
                'high': float(md.high_price),
                'low': float(md.low_price),
                'close': float(md.close_price),
                'volume': float(md.volume),
            })
        
        return JsonResponse({'data': data})
    except Symbol.DoesNotExist:
        return JsonResponse({'error': 'Symbol not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def get_technical_indicators(request, symbol_id):
    """Get technical indicators for a symbol"""
    try:
        symbol = Symbol.objects.get(id=symbol_id)
        indicators = TechnicalIndicator.objects.filter(symbol=symbol).order_by('-timestamp')[:50]
        
        data = {}
        for indicator in indicators:
            if indicator.indicator_type not in data:
                data[indicator.indicator_type] = []
            
            data[indicator.indicator_type].append({
                'timestamp': indicator.timestamp.isoformat(),
                'period': indicator.period,
                'value': float(indicator.value),
            })
        
        return JsonResponse({'data': data})
    except Symbol.DoesNotExist:
        return JsonResponse({'error': 'Symbol not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting technical indicators: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def sync_data_manual(request):
    """Manual data sync endpoint"""
    if request.method == 'POST':
        try:
            service = CryptoDataIngestionService()
            
            # Sync symbols
            symbols_success = service.sync_crypto_symbols()
            
            # Sync market data for first few symbols
            symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)[:5]
            market_success = True
            for symbol in symbols:
                if not service.sync_market_data(symbol):
                    market_success = False
            
            return JsonResponse({
                'symbols_synced': symbols_success,
                'market_data_synced': market_success,
                'message': 'Data sync completed'
            })
        except Exception as e:
            logger.error(f"Error in manual data sync: {e}")
            return JsonResponse({'error': 'Data sync failed'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def calculate_indicators_manual(request):
    """Manual indicator calculation endpoint"""
    if request.method == 'POST':
        try:
            service = TechnicalAnalysisService()
            
            # Calculate indicators for first few symbols
            symbols = Symbol.objects.filter(symbol_type='CRYPTO', is_active=True)[:5]
            success_count = 0
            
            for symbol in symbols:
                if service.calculate_all_indicators(symbol):
                    success_count += 1
            
            return JsonResponse({
                'symbols_processed': len(symbols),
                'successful_calculations': success_count,
                'message': 'Indicator calculation completed'
            })
        except Exception as e:
            logger.error(f"Error in manual indicator calculation: {e}")
            return JsonResponse({'error': 'Indicator calculation failed'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def data_dashboard(request):
    """Data dashboard view"""
    # Get active crypto symbols
    crypto_symbols = Symbol.objects.filter(
        symbol_type='CRYPTO',
        is_active=True
    )[:10]
    
    # Get recent market data
    recent_market_data = {}
    for symbol in crypto_symbols:
        latest_data = MarketData.objects.filter(symbol=symbol).order_by('-timestamp').first()
        if latest_data:
            recent_market_data[symbol.symbol] = {
                'price': float(latest_data.close_price),
                'change_24h': float(latest_data.close_price - latest_data.open_price),
                'volume': float(latest_data.volume),
                'timestamp': latest_data.timestamp
            }
    
    # Get recent technical indicators
    recent_indicators = {}
    for symbol in crypto_symbols:
        rsi = TechnicalIndicator.objects.filter(
            symbol=symbol,
            indicator_type='RSI',
            period=14
        ).order_by('-timestamp').first()
        
        if rsi:
            recent_indicators[symbol.symbol] = {
                'rsi': float(rsi.value),
                'timestamp': rsi.timestamp
            }
    
    # Get recent sync logs
    recent_syncs = DataSyncLog.objects.order_by('-completed_at')[:10]
    
    context = {
        'crypto_symbols': crypto_symbols,
        'recent_market_data': recent_market_data,
        'recent_indicators': recent_indicators,
        'recent_syncs': recent_syncs,
    }
    
    return render(request, 'data/dashboard.html', context)
