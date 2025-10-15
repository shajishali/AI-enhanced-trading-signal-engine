import time
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
from typing import Dict, List, Optional

import requests
from django.db import transaction
from django.utils import timezone

from apps.trading.models import Symbol
from apps.data.models import MarketData, HistoricalDataRange


logger = logging.getLogger(__name__)


class HistoricalDataManager:
    """Fetch, store, and track historical OHLCV data for futures trading backtesting.

    Responsibilities:
    - Chunked fetching from Binance Futures klines API per timeframe
    - Idempotent upsert to MarketData keyed by (symbol, timestamp, timeframe)
    - Range tracking via HistoricalDataRange
    - Simple rate limiting and retry logic
    """

    def __init__(self) -> None:
        # Use Binance Futures API for futures trading backtesting
        self.binance_api_base = "https://fapi.binance.com/fapi/v1/klines"
        self.base_delay_seconds = 0.2
        self.burst_every = 20
        self.burst_sleep = 2.0

        self.timeframes: Dict[str, Dict[str, int | str]] = {
            '1m': {'interval': '1m', 'max_days': 1},
            '5m': {'interval': '5m', 'max_days': 5},
            '15m': {'interval': '15m', 'max_days': 10},
            '1h': {'interval': '1h', 'max_days': 41},
            '4h': {'interval': '4h', 'max_days': 166},
            '1d': {'interval': '1d', 'max_days': 1000},
        }

        self.symbol_mapping: Dict[str, str] = {
            'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'BNB': 'BNBUSDT', 'SOL': 'SOLUSDT', 'XRP': 'XRPUSDT',
            'ADA': 'ADAUSDT', 'DOGE': 'DOGEUSDT', 'TRX': 'TRXUSDT', 'LINK': 'LINKUSDT', 'DOT': 'DOTUSDT',
            'MATIC': 'MATICUSDT', 'AVAX': 'AVAXUSDT', 'UNI': 'UNIUSDT', 'ATOM': 'ATOMUSDT', 'LTC': 'LTCUSDT',
            'BCH': 'BCHUSDT', 'ALGO': 'ALGOUSDT', 'VET': 'VETUSDT', 'FTM': 'FTMUSDT', 'ICP': 'ICPUSDT',
            'SAND': 'SANDUSDT', 'MANA': 'MANAUSDT', 'NEAR': 'NEARUSDT', 'APT': 'APTUSDT', 'OP': 'OPUSDT',
            'ARB': 'ARBUSDT', 'MKR': 'MKRUSDT', 'RUNE': 'RUNEUSDT', 'INJ': 'INJUSDT', 'STX': 'STXUSDT',
            'AAVE': 'AAVEUSDT', 'COMP': 'COMPUSDT', 'CRV': 'CRVUSDT', 'LDO': 'LDOUSDT', 'CAKE': 'CAKEUSDT',
            'PENDLE': 'PENDLEUSDT', 'DYDX': 'DYDXUSDT', 'FET': 'FETUSDT', 'CRO': 'CROUSDT', 'KCS': 'KCSUSDT',
            'OKB': 'OKBUSDT', 'LEO': 'LEOUSDT', 'QNT': 'QNTUSDT', 'HBAR': 'HBARUSDT', 'EGLD': 'EGLDUSDT',
            'FLOW': 'FLOWUSDT', 'SEI': 'SEIUSDT', 'TIA': 'TIAUSDT', 'GALA': 'GALAUSDT', 'GRT': 'GRTUSDT',
            'XMR': 'XMRUSDT', 'ZEC': 'ZECUSDT', 'DAI': 'DAIUSDT', 'TUSD': 'TUSDUSDT', 'GT': 'GTUSDT',
        }

    def fetch_complete_historical_data(
        self,
        symbol: Symbol,
        timeframe: str = '1h',
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> bool:
        """Fetch and persist historical OHLCV between start and end for a symbol/timeframe.

        If start/end are not provided, defaults to 2020-01-01 → now.
        """
        if timeframe not in self.timeframes:
            logger.error(f"Unsupported timeframe: {timeframe}")
            return False

        mapped = self.symbol_mapping.get(symbol.symbol.upper())
        if not mapped:
            logger.error(f"Symbol not supported for backfill: {symbol.symbol}")
            return False

        # Ensure all dates are UTC
        if start is None:
            start = datetime(2020, 1, 1, tzinfo=dt_timezone.utc)
        elif start.tzinfo is None:
            start = start.replace(tzinfo=dt_timezone.utc)
            
        if end is None:
            end = timezone.now()
        elif end.tzinfo is None:
            end = end.replace(tzinfo=dt_timezone.utc)

        max_days = int(self.timeframes[timeframe]['max_days'])
        interval = str(self.timeframes[timeframe]['interval'])

        current = start
        total_saved = 0
        request_count = 0

        while current < end:
            window_end = min(current + timedelta(days=max_days), end)
            klines = self._fetch_klines_chunk(mapped, current, window_end, interval)
            if klines:
                saved = self._save_market_data(symbol, timeframe, klines)
                total_saved += saved
                # Avoid Unicode arrows to be compatible with Windows console
                logger.info(
                    "Saved %s records for %s %s %s -> %s",
                    saved,
                    symbol.symbol,
                    timeframe,
                    str(current.date()),
                    str(window_end.date()),
                )

            current = window_end
            request_count += 1

            if request_count % self.burst_every == 0:
                time.sleep(self.burst_sleep)
            else:
                time.sleep(self.base_delay_seconds)

        self._update_range(symbol, timeframe, start, end, total_saved)
        logger.info("Backfill complete: %s %s, total_saved=%s", symbol.symbol, timeframe, total_saved)
        return True

    def _fetch_klines_chunk(self, mapped_symbol: str, start: datetime, end: datetime, interval: str) -> List[Dict]:
        """Fetch klines chunk with proper UTC handling"""
        # Ensure timestamps are UTC
        if start.tzinfo is None:
            start = start.replace(tzinfo=dt_timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=dt_timezone.utc)
            
        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)

        params = {
            'symbol': mapped_symbol,
            'interval': interval,
            'startTime': start_ms,
            'endTime': end_ms,
            'limit': 1000,
        }

        for attempt in range(3):
            try:
                resp = requests.get(self.binance_api_base, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                parsed: List[Dict] = []
                for k in data:
                    # Ensure timestamp is UTC
                    timestamp = datetime.fromtimestamp(k[0] / 1000, tz=dt_timezone.utc)
                    parsed.append({
                        'timestamp': timestamp,
                        'open': Decimal(str(k[1])),
                        'high': Decimal(str(k[2])),
                        'low': Decimal(str(k[3])),
                        'close': Decimal(str(k[4])),
                        'volume': Decimal(str(k[5])) if k[5] is not None else Decimal('0'),
                    })
                return parsed
            except Exception as e:
                delay = 0.5 * (2 ** attempt)
                logger.warning(f"Fetch attempt {attempt+1} failed: {e}; retrying in {delay:.1f}s")
                time.sleep(delay)

        logger.error("Failed to fetch klines after retries")
        return []

    def _save_market_data(self, symbol: Symbol, timeframe: str, records: List[Dict]) -> int:
        """Save market data with proper UTC timestamps"""
        saved = 0
        with transaction.atomic():
            for r in records:
                # Ensure timestamp is UTC
                timestamp = r['timestamp']
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=dt_timezone.utc)
                    
                _, created = MarketData.objects.update_or_create(
                    symbol=symbol,
                    timestamp=timestamp,
                    timeframe=timeframe,
                    defaults={
                        'open_price': r['open'],
                        'high_price': r['high'],
                        'low_price': r['low'],
                        'close_price': r['close'],
                        'volume': r['volume'],
                    }
                )
                if created:
                    saved += 1
        return saved

    def _update_range(self, symbol: Symbol, timeframe: str, start: datetime, end: datetime, total: int) -> None:
        """Update range tracking with UTC timestamps"""
        try:
            # Ensure timestamps are UTC
            if start.tzinfo is None:
                start = start.replace(tzinfo=dt_timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=dt_timezone.utc)
                
            HistoricalDataRange.objects.update_or_create(
                symbol=symbol,
                timeframe=timeframe,
                defaults={
                    'earliest_date': start,
                    'latest_date': end,
                    'total_records': total,
                    'is_complete': total > 0,
                }
            )
        except Exception as e:
            logger.error(f"Failed to update range tracking for {symbol.symbol} {timeframe}: {e}")


def get_historical_data_manager() -> HistoricalDataManager:
    return HistoricalDataManager()


