"""
Backtesting API Views
Handles coin name input, date period selection, and signal generation based on strategy
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from apps.trading.models import Symbol
from apps.signals.models import TradingSignal, SignalType
from apps.analytics.models import BacktestResult

logger = logging.getLogger(__name__)


class BacktestAPIView(View):
    """Main backtesting API endpoint"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle backtesting requests"""
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Handle form data
                data = request.POST
            
            # Extract parameters
            symbol_str = data.get('symbol', 'BTC').upper()
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            action = data.get('action', 'generate_signals')
            
            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now() - timedelta(days=365)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
            
            # Get or create symbol
            symbol = self._get_or_create_symbol(symbol_str)
            
            if action == 'generate_signals':
                return self._generate_historical_signals(request, symbol, start_date, end_date)
            elif action == 'backtest':
                return self._run_backtest(request, symbol, start_date, end_date)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
                
        except Exception as e:
            logger.error(f"Backtesting API error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _get_or_create_symbol(self, symbol_str: str) -> Symbol:
        """Get or create symbol object"""
        try:
            symbol, created = Symbol.objects.get_or_create(
                symbol=symbol_str,
                defaults={
                    'name': f'{symbol_str} Trading Pair',
                    'symbol_type': 'CRYPTO',
                    'is_crypto_symbol': True,
                    'is_spot_tradable': True,
                    'is_active': True
                }
            )
            return symbol
        except Exception as e:
            logger.error(f"Error getting/creating symbol {symbol_str}: {e}")
            raise
    
    def _generate_historical_signals(self, request, symbol, start_date, end_date):
        """Generate historical signals for the given period using YOUR actual strategy"""
        try:
            # Import the new strategy-based backtesting service
            from apps.signals.strategy_backtesting_service import StrategyBacktestingService
            
            # Create strategy backtesting service
            strategy_service = StrategyBacktestingService()
            
            # Generate signals based on YOUR actual strategy
            signals = strategy_service.generate_historical_signals(symbol, start_date, end_date)
            
            # Convert signals to the required format
            formatted_signals = []
            for signal in signals:
                formatted_signals.append({
                    'id': f"strategy_{hash(signal['created_at'])}",  # Generate unique ID
                    'symbol': str(signal['symbol']),
                    'signal_type': str(signal['signal_type']),
                    'strength': str(signal['strength']),
                    'confidence_score': float(signal['confidence_score']),
                    'entry_price': float(signal['entry_price']),
                    'target_price': float(signal['target_price']),
                    'stop_loss': float(signal['stop_loss']),
                    'risk_reward_ratio': float(signal['risk_reward_ratio']),
                    'timeframe': str(signal['timeframe']),
                    'quality_score': float(signal['quality_score']),
                    'created_at': str(signal['created_at']),
                    'is_executed': False,
                    'executed_at': None,
                    'strategy_confirmations': int(signal.get('strategy_confirmations', 0)),
                    'strategy_details': signal.get('strategy_details', {})
                })
            
            logger.info(f"Generated {len(formatted_signals)} signals using YOUR strategy for {symbol.symbol}")
            
            # Check if no signals were generated and provide helpful message
            no_signals_reason = None
            if len(formatted_signals) == 0:
                # Check if it's due to no historical data
                from apps.data.models import MarketData
                data_count = MarketData.objects.filter(
                    symbol=symbol,
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).count()
                
                if data_count == 0:
                    no_signals_reason = f"No historical data available for {symbol.symbol} in the selected date range ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}). Please try a different cryptocurrency or date range."
                else:
                    no_signals_reason = f"Your strategy analyzed {data_count} data points for {symbol.symbol} but found no signals meeting your criteria. This is normal - your strategy is selective and only generates high-quality signals."
            
            return JsonResponse({
                'success': True,
                'action': 'generate_signals',
                'signals': formatted_signals,
                'total_signals': len(formatted_signals),
                'symbol': symbol.symbol,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'strategy_used': 'YOUR_ACTUAL_STRATEGY',
                'no_signals_reason': no_signals_reason,
                'strategy_details': {
                    'take_profit_percentage': 15.0,
                    'stop_loss_percentage': 8.0,
                    'min_risk_reward_ratio': 1.5,
                    'rsi_buy_range': [20, 50],
                    'rsi_sell_range': [50, 80],
                    'volume_threshold': 1.2
                }
            })
            
        except Exception as e:
            logger.error(f"Error generating historical signals with YOUR strategy: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _run_backtest(self, request, symbol, start_date, end_date):
        """Run a full backtest"""
        try:
            # This would implement actual backtesting logic
            # For now, return a mock result
            return JsonResponse({
                'success': True,
                'action': 'backtest',
                'result': {
                    'total_return': 15.5,
                    'annualized_return': 12.3,
                    'sharpe_ratio': 1.2,
                    'max_drawdown': -8.5,
                    'win_rate': 65.0,
                    'total_trades': 25,
                    'winning_trades': 16,
                    'losing_trades': 9
                }
            })
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class BacktestSearchAPIView(View):
    """API for managing backtest searches"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """Get symbols or search history"""
        action = request.GET.get('action', 'symbols')
        
        if action == 'symbols':
            return self._get_symbols()
        elif action == 'history':
            return self._get_search_history(request)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
    
    def post(self, request):
        """Delete a search"""
        try:
            data = json.loads(request.body)
            search_id = data.get('search_id')
            
            if not search_id:
                return JsonResponse({'success': False, 'error': 'Search ID required'})
            
            # For now, just return success (no actual deletion)
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f"Error deleting search: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _get_symbols(self):
        """Get available symbols"""
        try:
            symbols = Symbol.objects.filter(
                is_crypto_symbol=True,
                is_active=True
            ).order_by('symbol')
            
            symbol_list = []
            for symbol in symbols:
                symbol_list.append({
                    'symbol': symbol.symbol,
                    'name': symbol.name,
                    'is_spot_tradable': symbol.is_spot_tradable
                })
            
            return JsonResponse({
                'success': True,
                'symbols': symbol_list
            })
            
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _get_search_history(self, request):
        """Get search history for the user"""
        try:
            # For now, return empty history
            return JsonResponse({
                'success': True,
                'searches': []
            })
            
        except Exception as e:
            logger.error(f"Error getting search history: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class TradingViewExportAPIView(View):
    """API for exporting signals to TradingView format"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Export signals to CSV for TradingView"""
        try:
            data = json.loads(request.body)
            
            symbol = data.get('symbol', 'BTC')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            # Get signals for the period
            symbol_obj = Symbol.objects.filter(symbol=symbol).first()
            if not symbol_obj:
                return JsonResponse({'success': False, 'error': 'Symbol not found'})
            
            # Get signals in the date range
            signals = TradingSignal.objects.filter(
                symbol=symbol_obj,
                created_at__date__range=[start_date.split('T')[0], end_date.split('T')[0]]
            ).order_by('created_at')
            
            # Generate CSV content
            csv_content = self._generate_csv_content(signals)
            
            filename = f"{symbol}_signals_{start_date.split('T')[0]}_to_{end_date.split('T')[0]}.csv"
            
            return JsonResponse({
                'success': True,
                'csv_content': csv_content,
                'filename': filename
            })
            
        except Exception as e:
            logger.error(f"Error exporting to TradingView: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generate_csv_content(self, signals):
        """Generate CSV content for signals"""
        headers = [
            'Timestamp', 'Symbol', 'Signal Type', 'Strength', 'Confidence',
            'Entry Price', 'Target Price', 'Stop Loss', 'Risk/Reward',
            'Timeframe', 'Quality Score'
        ]
        
        rows = [headers]
        
        for signal in signals:
            row = [
                signal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                signal.symbol.symbol,
                signal.signal_type.name if signal.signal_type else 'N/A',
                signal.strength,
                f"{signal.confidence_score:.2f}",
                str(signal.entry_price) if signal.entry_price else 'N/A',
                str(signal.target_price) if signal.target_price else 'N/A',
                str(signal.stop_loss) if signal.stop_loss else 'N/A',
                str(signal.risk_reward_ratio) if signal.risk_reward_ratio else 'N/A',
                signal.timeframe or 'N/A',
                str(signal.quality_score) if signal.quality_score else 'N/A'
            ]
            rows.append(row)
        
        # Convert to CSV format
        csv_lines = []
        for row in rows:
            csv_lines.append(','.join(f'"{str(cell)}"' for cell in row))
        
        return '\n'.join(csv_lines)
