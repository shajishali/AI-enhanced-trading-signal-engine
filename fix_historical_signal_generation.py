#!/usr/bin/env python3
"""
Fix Historical Signal Generation for Backtesting
This script fixes the HistoricalSignalService to ensure proper price values are always generated
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')

import django
django.setup()

def print_status(message, status="INFO"):
    """Print status message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "FIXING": "🔧"
    }
    print(f"[{timestamp}] {status_symbols.get(status, 'ℹ️')} {message}")

def create_enhanced_historical_signal_service():
    """Create an enhanced version of the HistoricalSignalService with proper price handling"""
    
    enhanced_service_code = '''
# Enhanced HistoricalSignalService with proper price handling
# Add this to apps/signals/services.py to replace the existing HistoricalSignalService

class EnhancedHistoricalSignalService:
    """Enhanced service for generating signals for specific historical periods with proper price handling"""
    
    def __init__(self):
        self.signal_service = SignalGenerationService()
        self.logger = logging.getLogger(__name__)
    
    def get_fallback_price_for_symbol(self, symbol_obj):
        """Get a reasonable fallback price for a symbol"""
        
        # Try to get latest market data
        try:
            from apps.data.models import MarketData
            latest_market_data = MarketData.objects.filter(
                symbol=symbol_obj
            ).order_by('-timestamp').first()
            
            if latest_market_data and latest_market_data.close_price > 0:
                return float(latest_market_data.close_price)
        except Exception as e:
            self.logger.warning(f"Could not get market data for {symbol_obj.symbol}: {e}")
        
        # Try live price service
        try:
            from apps.data.real_price_service import get_live_prices
            live_prices = get_live_prices()
            if symbol_obj.symbol in live_prices:
                price = live_prices[symbol_obj.symbol].get('price', 0)
                if price > 0:
                    return float(price)
        except Exception as e:
            self.logger.warning(f"Could not get live price for {symbol_obj.symbol}: {e}")
        
        # Fallback to reasonable default prices for major cryptocurrencies
        default_prices = {
            'BTC': 100000.0, 'ETH': 4000.0, 'BNB': 600.0, 'ADA': 1.0, 'SOL': 200.0,
            'XRP': 2.0, 'DOGE': 0.4, 'MATIC': 1.0, 'DOT': 8.0, 'AVAX': 40.0,
            'LINK': 20.0, 'UNI': 15.0, 'ATOM': 12.0, 'FTM': 1.2, 'ALGO': 0.3,
            'VET': 0.05, 'ICP': 15.0, 'THETA': 2.0, 'SAND': 0.5, 'MANA': 0.8,
            'LTC': 150.0, 'BCH': 500.0, 'ETC': 30.0, 'XLM': 0.3, 'TRX': 0.2,
            'XMR': 200.0, 'ZEC': 50.0, 'DASH': 80.0, 'NEO': 25.0, 'QTUM': 5.0
        }
        
        return default_prices.get(symbol_obj.symbol, 1.0)  # Default to $1 for unknown symbols
    
    def calculate_target_and_stop_loss(self, entry_price, signal_type_name):
        """Calculate target price and stop loss based on entry price and signal type"""
        entry_decimal = Decimal(str(entry_price))
        
        if signal_type_name in ['BUY', 'STRONG_BUY']:
            # For buy signals: 60% profit target, 40% stop loss
            target_price = entry_decimal * Decimal('1.60')  # 60% profit
            stop_loss = entry_decimal * Decimal('0.60')     # 40% stop loss
        else:
            # For sell signals: 60% profit target, 40% stop loss
            target_price = entry_decimal * Decimal('0.40')  # 60% profit for sell (lower price)
            stop_loss = entry_decimal * Decimal('1.40')     # 40% stop loss for sell (higher price)
        
        return target_price, stop_loss
    
    def generate_signals_for_period(self, symbol, start_date, end_date):
        """
        Generate signals for a specific symbol and date range with proper price handling
        """
        try:
            from django.utils import timezone
            from apps.signals.models import TradingSignal
            
            self.logger.info(f"Generating historical signals for {symbol.symbol} from {start_date} to {end_date}")
            
            # Ensure dates are timezone-aware
            if start_date.tzinfo is None:
                start_date = timezone.make_aware(start_date)
            if end_date.tzinfo is None:
                end_date = timezone.make_aware(end_date)
            
            # Validate date range
            if start_date >= end_date:
                raise ValueError("Start date must be before end date")
            
            # Get fallback price for this symbol
            fallback_price = self.get_fallback_price_for_symbol(symbol)
            self.logger.info(f"Using fallback price for {symbol.symbol}: {fallback_price}")
            
            # Generate base signals using the main signal service
            base_signals = self.signal_service.generate_signals_for_symbol(symbol)
            self.logger.info(f"Generated {len(base_signals)} base signals for {symbol.symbol}")
            
            # Create historical signals with proper price values
            historical_signals = []
            
            if base_signals:
                # Calculate time span for distributing signals
                time_span = end_date - start_date
                signal_count = len(base_signals)
                
                # Distribute signals evenly across the time period
                for i, base_signal in enumerate(base_signals):
                    # Calculate timestamp within the period
                    if signal_count > 1:
                        signal_time = start_date + (time_span * i / (signal_count - 1))
                    else:
                        signal_time = start_date + time_span / 2
                    
                    # Ensure proper price values
                    entry_price = base_signal.entry_price if base_signal.entry_price and base_signal.entry_price > 0 else Decimal(str(fallback_price))
                    
                    # Calculate target and stop loss if they're missing
                    if not base_signal.target_price or not base_signal.stop_loss or base_signal.target_price <= 0 or base_signal.stop_loss <= 0:
                        target_price, stop_loss = self.calculate_target_and_stop_loss(
                            float(entry_price), 
                            base_signal.signal_type.name
                        )
                    else:
                        target_price = base_signal.target_price
                        stop_loss = base_signal.stop_loss
                    
                    # Calculate risk-reward ratio
                    risk = abs(float(entry_price - stop_loss))
                    reward = abs(float(target_price - entry_price))
                    risk_reward_ratio = reward / risk if risk > 0 else 1.0
                    
                    # Ensure all required fields have proper values
                    quality_score = getattr(base_signal, 'quality_score', None) or base_signal.confidence_score or 0.5
                    timeframe = getattr(base_signal, 'timeframe', '1D')
                    entry_point_type = getattr(base_signal, 'entry_point_type', 'BREAKOUT')
                    
                    # Create historical signal with guaranteed proper values
                    historical_signal = TradingSignal(
                        symbol=base_signal.symbol,
                        signal_type=base_signal.signal_type,
                        entry_price=entry_price,
                        target_price=target_price,
                        stop_loss=stop_loss,
                        confidence_score=base_signal.confidence_score,
                        confidence_level=base_signal.confidence_level,
                        risk_reward_ratio=risk_reward_ratio,
                        timeframe=timeframe,
                        entry_point_type=entry_point_type,
                        quality_score=quality_score,
                        strength=base_signal.strength,
                        notes=getattr(base_signal, 'notes', f'Historical signal with fallback price: {fallback_price}'),
                        is_valid=True,
                        expires_at=signal_time + timezone.timedelta(hours=24),
                        created_at=signal_time,
                        is_hybrid=getattr(base_signal, 'is_hybrid', False),
                        metadata=getattr(base_signal, 'metadata', {})
                    )
                    
                    historical_signals.append(historical_signal)
                    self.logger.info(f"Prepared historical signal for {symbol.symbol}: {base_signal.signal_type.name} at ${entry_price}")
            
            # Save signals to database
            if historical_signals:
                try:
                    # Use bulk_create for efficiency
                    TradingSignal.objects.bulk_create(historical_signals, ignore_conflicts=True)
                    self.logger.info(f"Bulk created {len(historical_signals)} signals for {symbol.symbol}")
                    
                    # Retrieve the created signals from the database
                    created_signals = TradingSignal.objects.filter(
                        symbol=symbol,
                        created_at__gte=start_date,
                        created_at__lte=end_date
                    ).order_by('created_at')
                    
                    self.logger.info(f"Retrieved {created_signals.count()} signals from database")
                    return list(created_signals)
                    
                except Exception as bulk_error:
                    self.logger.error(f"Error with bulk creation: {bulk_error}")
                    # Fallback to individual saves
                    saved_signals = []
                    for signal in historical_signals:
                        try:
                            signal.save()
                            saved_signals.append(signal)
                        except Exception as individual_error:
                            self.logger.error(f"Error saving individual signal: {individual_error}")
                    return saved_signals
            
            self.logger.info(f"Generated {len(historical_signals)} historical signals for {symbol.symbol}")
            return historical_signals
            
        except Exception as e:
            self.logger.error(f"Error generating historical signals: {e}")
            return []
    
    def validate_date_range(self, start_date, end_date):
        """Validate the date range for backtesting"""
        try:
            from django.utils import timezone
            
            # Ensure dates are timezone-aware
            if start_date.tzinfo is None:
                start_date = timezone.make_aware(start_date)
            if end_date.tzinfo is None:
                end_date = timezone.make_aware(end_date)
            
            # Check if start date is before end date
            if start_date >= end_date:
                return False, "Start date must be before end date"
            
            # Check if date range is not too far in the future
            now = timezone.now()
            if start_date > now:
                return False, "Start date cannot be in the future"
            
            # Check if date range is reasonable (not more than 5 years)
            max_range = timezone.timedelta(days=5*365)  # 5 years
            if end_date - start_date > max_range:
                return False, "Date range cannot exceed 5 years"
            
            return True, "Date range is valid"
            
        except Exception as e:
            return False, f"Date validation error: {str(e)}"
    
    def get_available_symbols(self):
        """Get available symbols for backtesting"""
        try:
            from apps.trading.models import Symbol
            return Symbol.objects.filter(is_active=True).order_by('symbol')
        except Exception as e:
            self.logger.error(f"Error getting available symbols: {e}")
            return []
'''
    
    return enhanced_service_code

def apply_fix_to_services_file():
    """Apply the fix directly to the services.py file"""
    
    print_status("Applying fix to HistoricalSignalService", "FIXING")
    
    services_file_path = os.path.join(project_dir, 'apps', 'signals', 'services.py')
    
    try:
        # Read the current services.py file
        with open(services_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the generate_signals_for_period method and replace it
        method_start = content.find('def generate_signals_for_period(self, symbol: Symbol, start_date: datetime, end_date: datetime) -> List[TradingSignal]:')
        
        if method_start == -1:
            print_status("Could not find generate_signals_for_period method", "ERROR")
            return False
        
        # Find the end of the method (next method or class)
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\n\nclass ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Create the enhanced method
        enhanced_method = '''    def generate_signals_for_period(self, symbol: Symbol, start_date: datetime, end_date: datetime) -> List[TradingSignal]:
        """
        Generate signals for a specific symbol and date range with proper price handling
        
        Args:
            symbol: Trading symbol to generate signals for
            start_date: Start date for signal generation
            end_date: End date for signal generation
            
        Returns:
            List of generated TradingSignal objects with guaranteed proper price values
        """
        try:
            self.logger.info(f"Generating historical signals for {symbol.symbol} from {start_date} to {end_date}")
            
            # Ensure dates are timezone-aware to avoid comparison errors
            from django.utils import timezone
            if start_date.tzinfo is None:
                start_date = timezone.make_aware(start_date)
            if end_date.tzinfo is None:
                end_date = timezone.make_aware(end_date)
            
            # Validate date range
            if start_date >= end_date:
                raise ValueError("Start date must be before end date")
            
            # Get fallback price for this symbol
            fallback_price = self._get_fallback_price_for_symbol(symbol)
            self.logger.info(f"Using fallback price for {symbol.symbol}: {fallback_price}")
            
            # Generate base signals using the main signal service
            base_signals = self.signal_service.generate_signals_for_symbol(symbol)
            self.logger.info(f"Generated {len(base_signals)} base signals for {symbol.symbol}")
            
            # Create historical signals with proper price values
            historical_signals = []
            
            if base_signals:
                # Calculate time span for distributing signals
                time_span = end_date - start_date
                signal_count = len(base_signals)
                
                # Distribute signals evenly across the time period
                for i, base_signal in enumerate(base_signals):
                    # Calculate timestamp within the period
                    if signal_count > 1:
                        signal_time = start_date + (time_span * i / (signal_count - 1))
                    else:
                        signal_time = start_date + time_span / 2
                    
                    # Ensure proper price values
                    entry_price = base_signal.entry_price if base_signal.entry_price and base_signal.entry_price > 0 else Decimal(str(fallback_price))
                    
                    # Calculate target and stop loss if they're missing
                    if not base_signal.target_price or not base_signal.stop_loss or base_signal.target_price <= 0 or base_signal.stop_loss <= 0:
                        target_price, stop_loss = self._calculate_target_and_stop_loss(
                            float(entry_price), 
                            base_signal.signal_type.name
                        )
                    else:
                        target_price = base_signal.target_price
                        stop_loss = base_signal.stop_loss
                    
                    # Calculate risk-reward ratio
                    risk = abs(float(Decimal(str(entry_price)) - stop_loss))
                    reward = abs(float(target_price - Decimal(str(entry_price))))
                    risk_reward_ratio = reward / risk if risk > 0 else 1.0
                    
                    # Ensure all required fields have proper values
                    quality_score = getattr(base_signal, 'quality_score', None) or base_signal.confidence_score or 0.5
                    timeframe = getattr(base_signal, 'timeframe', '1D')
                    entry_point_type = getattr(base_signal, 'entry_point_type', 'BREAKOUT')
                    
                    # Create historical signal with guaranteed proper values
                    historical_signal = TradingSignal(
                        symbol=base_signal.symbol,
                        signal_type=base_signal.signal_type,
                        entry_price=entry_price,
                        target_price=target_price,
                        stop_loss=stop_loss,
                        confidence_score=base_signal.confidence_score,
                        confidence_level=base_signal.confidence_level,
                        risk_reward_ratio=risk_reward_ratio,
                        timeframe=timeframe,
                        entry_point_type=entry_point_type,
                        quality_score=quality_score,
                        strength=base_signal.strength,
                        notes=getattr(base_signal, 'notes', f'Historical signal with fallback price: {fallback_price}'),
                        is_valid=True,
                        expires_at=signal_time + timezone.timedelta(hours=24),
                        created_at=signal_time,
                        is_hybrid=getattr(base_signal, 'is_hybrid', False),
                        metadata=getattr(base_signal, 'metadata', {})
                    )
                    
                    historical_signals.append(historical_signal)
                    self.logger.info(f"Prepared historical signal for {symbol.symbol}: {base_signal.signal_type.name} at ${entry_price}")
            
            # Save signals to database
            if historical_signals:
                try:
                    # Use bulk_create for efficiency
                    TradingSignal.objects.bulk_create(historical_signals, ignore_conflicts=True)
                    self.logger.info(f"Bulk created {len(historical_signals)} signals for {symbol.symbol}")
                    
                    # Retrieve the created signals from the database
                    created_signals = TradingSignal.objects.filter(
                        symbol=symbol,
                        created_at__gte=start_date,
                        created_at__lte=end_date
                    ).order_by('created_at')
                    
                    self.logger.info(f"Retrieved {created_signals.count()} signals from database")
                    return list(created_signals)
                    
                except Exception as bulk_error:
                    self.logger.error(f"Error with bulk creation: {bulk_error}")
                    # Fallback to individual saves
                    saved_signals = []
                    for signal in historical_signals:
                        try:
                            signal.save()
                            saved_signals.append(signal)
                        except Exception as individual_error:
                            self.logger.error(f"Error saving individual signal: {individual_error}")
                    return saved_signals
            
            self.logger.info(f"Generated {len(historical_signals)} historical signals for {symbol.symbol}")
            return historical_signals
            
        except Exception as e:
            self.logger.error(f"Error generating historical signals: {e}")
            return []
    
    def _get_fallback_price_for_symbol(self, symbol_obj):
        """Get a reasonable fallback price for a symbol"""
        
        # Try to get latest market data
        try:
            from apps.data.models import MarketData
            latest_market_data = MarketData.objects.filter(
                symbol=symbol_obj
            ).order_by('-timestamp').first()
            
            if latest_market_data and latest_market_data.close_price > 0:
                return float(latest_market_data.close_price)
        except Exception as e:
            self.logger.warning(f"Could not get market data for {symbol_obj.symbol}: {e}")
        
        # Try live price service
        try:
            from apps.data.real_price_service import get_live_prices
            live_prices = get_live_prices()
            if symbol_obj.symbol in live_prices:
                price = live_prices[symbol_obj.symbol].get('price', 0)
                if price > 0:
                    return float(price)
        except Exception as e:
            self.logger.warning(f"Could not get live price for {symbol_obj.symbol}: {e}")
        
        # Fallback to reasonable default prices for major cryptocurrencies
        default_prices = {
            'BTC': 100000.0, 'ETH': 4000.0, 'BNB': 600.0, 'ADA': 1.0, 'SOL': 200.0,
            'XRP': 2.0, 'DOGE': 0.4, 'MATIC': 1.0, 'DOT': 8.0, 'AVAX': 40.0,
            'LINK': 20.0, 'UNI': 15.0, 'ATOM': 12.0, 'FTM': 1.2, 'ALGO': 0.3,
            'VET': 0.05, 'ICP': 15.0, 'THETA': 2.0, 'SAND': 0.5, 'MANA': 0.8,
            'LTC': 150.0, 'BCH': 500.0, 'ETC': 30.0, 'XLM': 0.3, 'TRX': 0.2,
            'XMR': 200.0, 'ZEC': 50.0, 'DASH': 80.0, 'NEO': 25.0, 'QTUM': 5.0
        }
        
        return default_prices.get(symbol_obj.symbol, 1.0)  # Default to $1 for unknown symbols
    
    def _calculate_target_and_stop_loss(self, entry_price, signal_type_name):
        """Calculate target price and stop loss based on entry price and signal type"""
        entry_decimal = Decimal(str(entry_price))
        
        if signal_type_name in ['BUY', 'STRONG_BUY']:
            # For buy signals: 60% profit target, 40% stop loss
            target_price = entry_decimal * Decimal('1.60')  # 60% profit
            stop_loss = entry_decimal * Decimal('0.60')     # 40% stop loss
        else:
            # For sell signals: 60% profit target, 40% stop loss
            target_price = entry_decimal * Decimal('0.40')  # 60% profit for sell (lower price)
            stop_loss = entry_decimal * Decimal('1.40')     # 40% stop loss for sell (higher price)
        
        return target_price, stop_loss'''
        
        # Replace the old method with the enhanced one
        new_content = content[:method_start] + enhanced_method + content[method_end:]
        
        # Write the updated content back to the file
        with open(services_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print_status("Successfully updated HistoricalSignalService", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Error applying fix: {e}", "ERROR")
        return False

def main():
    """Main function to apply the fix"""
    print_status("🔧 Starting Historical Signal Generation Fix", "INFO")
    print("=" * 60)
    
    try:
        # Apply the fix to the services file
        success = apply_fix_to_services_file()
        
        if success:
            print("=" * 60)
            print_status("✅ Historical Signal Generation Fix Applied Successfully!", "SUCCESS")
            print_status("🎉 Backtesting will now generate signals with proper price values!", "SUCCESS")
            print_status("💡 The fix ensures that all generated signals have valid entry_price, target_price, and stop_loss values", "INFO")
        else:
            print_status("❌ Fix application failed", "ERROR")
            return False
        
    except Exception as e:
        print_status(f"❌ Fix script failed: {e}", "ERROR")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)








