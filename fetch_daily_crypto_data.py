#!/usr/bin/env python3
"""
Daily Crypto Data Fetcher
Fetches daily OHLC data for all USDT pairs from 2020 to October 14, 2025
"""

import os
import sys
import django
import requests
import time
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from apps.data.models import MarketData, DataSource
from apps.trading.models import Symbol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_data_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.binance_source, _ = DataSource.objects.get_or_create(
            name="Binance API",
            defaults={
                'source_type': 'API',
                'url': 'https://api.binance.com',
                'is_active': True
            }
        )
        
    def get_usdt_symbols(self):
        """Get all USDT trading pairs from the database"""
        symbols = Symbol.objects.filter(symbol__endswith='USDT').exclude(symbol='USDT')
        logger.info(f"Found {symbols.count()} USDT trading pairs")
        return symbols
    
    def fetch_daily_data(self, symbol, start_date, end_date):
        """Fetch daily OHLC data for a specific symbol"""
        symbol_name = symbol.symbol
        
        # Convert dates to milliseconds timestamp
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)
        
        params = {
            'symbol': symbol_name,
            'interval': '1d',  # Daily data
            'startTime': start_ts,
            'endTime': end_ts,
            'limit': 1000  # Maximum limit per request
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Fetched {len(data)} daily records for {symbol_name}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {symbol_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error for {symbol_name}: {e}")
            return []
    
    def save_market_data(self, symbol, kline_data):
        """Save kline data to database"""
        saved_count = 0
        skipped_count = 0
        
        for kline in kline_data:
            try:
                # Parse kline data
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                open_price = Decimal(str(kline[1]))
                high_price = Decimal(str(kline[2]))
                low_price = Decimal(str(kline[3]))
                close_price = Decimal(str(kline[4]))
                volume = Decimal(str(kline[5]))
                
                # Check if record already exists
                existing_record = MarketData.objects.filter(
                    symbol=symbol,
                    timestamp=timestamp,
                    timeframe='1d'
                ).first()
                
                if existing_record:
                    # Update existing record
                    existing_record.open_price = open_price
                    existing_record.high_price = high_price
                    existing_record.low_price = low_price
                    existing_record.close_price = close_price
                    existing_record.volume = volume
                    existing_record.source = self.binance_source
                    existing_record.save()
                    logger.debug(f"Updated record for {symbol.symbol} on {timestamp.date()}")
                else:
                    # Create new record
                    MarketData.objects.create(
                        symbol=symbol,
                        timestamp=timestamp,
                        open_price=open_price,
                        high_price=high_price,
                        low_price=low_price,
                        close_price=close_price,
                        volume=volume,
                        source=self.binance_source,
                        timeframe='1d',
                        created_at=datetime.now()
                    )
                    logger.debug(f"Created new record for {symbol.symbol} on {timestamp.date()}")
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving data for {symbol.symbol}: {e}")
                skipped_count += 1
                continue
        
        logger.info(f"Saved {saved_count} records, skipped {skipped_count} records for {symbol.symbol}")
        return saved_count, skipped_count
    
    def fetch_all_symbols_data(self, start_date, end_date):
        """Fetch data for all USDT symbols"""
        symbols = self.get_usdt_symbols()
        total_saved = 0
        total_skipped = 0
        
        logger.info(f"Starting data fetch for {symbols.count()} symbols from {start_date.date()} to {end_date.date()}")
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"Processing {i}/{symbols.count()}: {symbol.symbol}")
            
            # Fetch data for this symbol
            kline_data = self.fetch_daily_data(symbol, start_date, end_date)
            
            if kline_data:
                saved, skipped = self.save_market_data(symbol, kline_data)
                total_saved += saved
                total_skipped += skipped
            else:
                logger.warning(f"No data fetched for {symbol.symbol}")
            
            # Rate limiting - be respectful to the API
            time.sleep(0.1)  # 100ms delay between requests
        
        logger.info(f"Data fetch completed. Total saved: {total_saved}, Total skipped: {total_skipped}")
        return total_saved, total_skipped
    
    def get_date_ranges(self, start_date, end_date):
        """Split date range into chunks to handle API limits"""
        ranges = []
        current_start = start_date
        
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=365), end_date)
            ranges.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)
        
        return ranges

def main():
    """Main function to fetch all historical data"""
    fetcher = CryptoDataFetcher()
    
    # Define date range: 2020 to October 14, 2025
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 10, 14)
    
    logger.info(f"Starting comprehensive data fetch from {start_date.date()} to {end_date.date()}")
    
    # Get date ranges to handle large time periods
    date_ranges = fetcher.get_date_ranges(start_date, end_date)
    
    total_saved = 0
    total_skipped = 0
    
    for i, (range_start, range_end) in enumerate(date_ranges, 1):
        logger.info(f"Processing date range {i}/{len(date_ranges)}: {range_start.date()} to {range_end.date()}")
        
        saved, skipped = fetcher.fetch_all_symbols_data(range_start, range_end)
        total_saved += saved
        total_skipped += skipped
        
        # Longer delay between date ranges
        if i < len(date_ranges):
            logger.info("Waiting 2 seconds before next date range...")
            time.sleep(2)
    
    logger.info(f"=== FINAL SUMMARY ===")
    logger.info(f"Total records saved: {total_saved}")
    logger.info(f"Total records skipped: {total_skipped}")
    logger.info(f"Data fetch completed successfully!")

if __name__ == "__main__":
    main()
