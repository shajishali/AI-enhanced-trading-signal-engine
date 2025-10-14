## Backtesting Database – Phased Plan (2020 → 2025-09) 

This document defines the phases to build, populate, validate, and operate a dedicated historical OHLCV database for crypto backtesting. Target coverage: all supported crypto symbols, from 2020-01-01 through 2025-09-30, with ongoing automated monthly updates.

---

### Phase 0 — Prerequisites and Scope
- Define supported symbols universe (Spot USDT pairs on Binance + any project-specific list).
- Choose timeframes to persist: 1m (optional), 5m (optional), 15m, 1h, 4h, 1d. Primary backtesting timeframe: 1h.
- Confirm storage budget and retention: keep at least 3–5 years of 1h, 1–2 years of 1m/5m if enabled, 5+ years of 1d.
- Verify API quota limits and add simple rate-limiting and retry policies.

Configuration (Phase 0 outcomes):

```
Symbols Universe (initial):
- Core (Top 30): BTC, ETH, BNB, SOL, XRP, ADA, DOGE, TRX, LINK, DOT,
  MATIC, AVAX, UNI, ATOM, LTC, BCH, ALGO, VET, FTM, ICP,
  SAND, MANA, NEAR, APT, OP, ARB, MKR, RUNE, INJ, STX
- Extended: all other active USDT spot pairs supported by Binance (added iteratively)

Timeframes to Persist:
- Required: 1h, 1d
- Optional: 15m, 4h (enable per storage budget)
- Experimental: 1m, 5m (disabled by default)

Historical Window:
- Start: 2020-01-01 00:00:00 UTC
- End:   2025-09-30 23:59:59 UTC (initial load)

Retention Policy:
- 1m/5m: keep 12 months
- 15m/1h: keep 24 months (min), target 36–60 months where storage allows
- 4h/1d: keep 5+ years

API and Rate Limits:
- Exchange: Binance REST `klines`
- Base interval delay: 200ms between requests
- Retries: 3 attempts with exponential backoff (0.5s, 1s, 2s)
- Burst control: sleep 2s every 20 requests

Backfilling Strategy:
- 1d timeframe: fetch in large date chunks
- 1h timeframe: 30–45-day chunks
- Resume-safe: idempotent upsert keyed by (symbol, timestamp, timeframe)

Data Validation Targets:
- Completeness: ≥ 99% per month per symbol/timeframe
- Timezone: all timestamps in UTC
- Numeric integrity: OHLCV >= 0, volume nullable → 0
```

Deliverables:
- Symbols manifest and timeframe policy.
- Environment config with API keys and rate limits.

---

### Phase 1 — Data Model and Migrations
- Add `timeframe` field to `MarketData`.
- Strengthen uniqueness: (`symbol`, `timestamp`, `timeframe`).
- Add composite indexes: (`symbol`, `timestamp`, `timeframe`).
- Create tracking tables:
  - `HistoricalDataRange(symbol, timeframe, earliest_date, latest_date, total_records, is_complete, last_synced)`
  - `DataQuality(symbol, timeframe, date_range_start, date_range_end, expected_records, actual_records, missing_records, completeness_percentage, has_gaps, has_anomalies, checked_at)`

Deliverables:
- Django migrations shipped and applied.

Status: IMPLEMENTED
- Files updated:
  - `apps/data/models.py`
    - `MarketData`: added `timeframe` and updated unique/indexes to (`symbol`, `timestamp`, `timeframe`).
    - Added `HistoricalDataRange` and `DataQuality` models.
- How to apply:
```
python manage.py makemigrations
python manage.py migrate
```

---

### Phase 2 — Historical Data Manager (Fetcher + Writer)
- Build `HistoricalDataManager` with:
  - Symbol mapping to exchange symbols (e.g., BTC → BTCUSDT).
  - Chunked fetch by timeframe respecting exchange `limit` and backfilling in ranges.
  - Robust parsing to OHLCV with UTC timestamps.
  - Idempotent upsert to `MarketData` using `update_or_create`.
  - Range tracking updates in `HistoricalDataRange`.
- Support timeframes: 1h and 1d initially; 15m/4h optional.

Deliverables:
- Service module with tested chunked fetch + upsert.

Status: IMPLEMENTED
- File: `apps/data/historical_data_manager.py`
- Features:
  - Binance klines fetch with retry/backoff and rate limiting
  - Chunked backfill windows per timeframe (e.g., 41 days for 1h)
  - Idempotent upsert to `MarketData` including `timeframe`
  - Range tracking via `HistoricalDataRange`

---

### Phase 3 — One-Time Backfill (2020-01-01 → 2025-09-30)
- Management command: `populate_historical_data` with args: `--symbol`, `--years` or date range, `--timeframe`.
- Strategy:
  - For each active symbol, fetch in chunks per timeframe:
    - 1d: entire window in few calls.
    - 1h: 30–45 days per chunk; loop until 2025-09-30.
  - Rate-limit (e.g., 200ms) and retry (exponential backoff) on 429/5xx.
- Run order:
  1. Top-20 symbols end-to-end (1d + 1h).
  2. Remaining symbols batch-wise.
- Progress logging to `DataSyncLog`.

Deliverables:
- Backfilled OHLCV for the whole period and tracked ranges per symbol/timeframe.

Status: IMPLEMENTED
- File: `apps/data/management/commands/populate_historical_data.py`
- Usage examples:
```
# BTC only, 1h, full window
python manage.py populate_historical_data --symbol BTC --timeframe 1h --start 2020-01-01

# All active symbols, 1d, limit first 30 symbols
python manage.py populate_historical_data --timeframe 1d --start 2020-01-01 --limit 30

# Full run (can be split into batches)
python manage.py populate_historical_data --timeframe 1d --start 2020-01-01
python manage.py populate_historical_data --timeframe 1h --start 2020-01-01
```

---

### Phase 4 — Data Quality Validation and Gap Filling
- Quality check function:
  - Calculate expected record count for a timeframe over a date range.
  - Detect gaps by timestamp deltas vs expected interval.
  - Store results in `DataQuality`.
- Gap filler:
  - For each gap window, re-fetch missing klines and upsert.
  - Repeat until no gaps or max retries reached.

Deliverables:
- Quality report (completeness %) per symbol/timeframe; gaps filled for 2020–2025-09.

Status: IMPLEMENTED
- Files:
  - `apps/data/management/commands/check_data_quality.py`
  - `apps/data/management/commands/fill_data_gaps.py`
- Usage:
```
# Check completeness for BTC last 365 days (1h)
python manage.py check_data_quality --symbol BTC --timeframe 1h --days 365

# Fill gaps for BTC (1h)
python manage.py fill_data_gaps --symbol BTC --timeframe 1h

# Batch check/fill (first 20 active symbols)
python manage.py check_data_quality --timeframe 1h --days 90 --limit 20
python manage.py fill_data_gaps --timeframe 1h --limit 20
```

---

### Phase 5 — Monthly Incremental Updates (Automation)
- Celery beat jobs:
  - Daily incremental updater (fetch last 2–3 days for safety) per symbol/timeframe.
  - Monthly consolidator: validate previous month completeness and fill gaps.
- Retention policy:
  - Keep ≥5 years 1d, ≥2 years 1h, ≥1 year 1m/5m (if enabled).
  - Cleanup task prunes beyond retention by timeframe.

Deliverables:
- Two scheduled tasks: `update_historical_data_task` (daily) and `check_and_fill_gaps_task` (weekly/monthly).

Status: IMPLEMENTED
- Files updated: `apps/data/tasks.py`
  - `update_historical_data_task`: daily, fetch last 2 days (1h) for all active symbols.
  - `weekly_gap_check_and_fill_task`: weekly, validate last 90 days and fill gaps.
  - `cleanup_old_data_task`: retention by timeframe (1m: 12mo, 1h: 24mo, 1d: 60mo).
- Beat schedule (example):
```
# In celery beat configuration (example)
app.conf.beat_schedule.update({
    'historical-incremental-daily': {
        'task': 'apps.data.tasks.update_historical_data_task',
        'schedule': crontab(hour=2, minute=0),
    },
    'historical-weekly-gap-check': {
        'task': 'apps.data.tasks.weekly_gap_check_and_fill_task',
        'schedule': crontab(hour=3, minute=0, day_of_week='sun'),
    },
    'historical-cleanup-monthly': {
        'task': 'apps.data.tasks.cleanup_old_data_task',
        'schedule': crontab(hour=4, minute=0, day_of_month='1'),
    },
})
```

---

### Phase 6 — Backtesting Integration (Real Data Only)
- Update backtesting services to query `MarketData` only; remove synthetic data fallbacks.
- If requested range missing, return a clear error and instructions to populate.
- Ensure dataframe indices use UTC and are continuous per timeframe.

Deliverables:
- Deterministic, real-data-only backtests; consistent results across runs.

Status: IMPLEMENTED
- Synthetic data fallbacks removed/disabled:
  - `apps/analytics/services.py` `_get_historical_data`: returns empty DataFrame with clear error if missing.
  - `apps/signals/backtesting_service.py` `_get_historical_data`: returns empty DataFrame with clear error.
  - `apps/signals/comprehensive_backtesting_service.py` `_get_historical_data`: returns empty DataFrame with clear error.
  - `apps/signals/services.py` `_get_historical_data`: logs error when QS empty.
- Behavior:
  - If data missing for a period, services instruct to populate historical data via management commands.

---

### Phase 7 — Monitoring & Observability
- Dashboards/metrics:
  - Coverage per symbol/timeframe (% completeness for last 30/90/365 days).
  - Last sync time; API error rates; retry counts.
- Alerts when completeness < 99% or last sync > 48h.

Deliverables:
- Health checks and lightweight reporting.

---

## Operations Runbook

### Initial Load (recommended order)
1) Apply migrations
2) Populate 1d for all symbols (2020→2025-09)
3) Populate 1h for top symbols, then the rest
4) Run quality check and gap filler

Example commands:
```
python manage.py makemigrations && python manage.py migrate

# Top symbols first (faster validation loop)
python manage.py populate_historical_data --symbol BTC --timeframe 1d --years 6
python manage.py populate_historical_data --symbol BTC --timeframe 1h --years 6

# Batch process (slice by is_active order)
python manage.py populate_historical_data --timeframe 1d --years 6
python manage.py populate_historical_data --timeframe 1h --years 6

# (Optional) Run data quality checks
python manage.py check_data_quality --symbol BTC --timeframe 1h --days 365
```

### Scheduled Automation
- Celery beat:
  - `update_historical_data_task`: daily at 02:00 UTC (fetch last 2–3 days).
  - `check_and_fill_gaps_task`: weekly on Sun 03:00 UTC (validate last 90 days, fill gaps).
- Ensure workers are running:
```
celery -A ai_trading_engine worker -l info --pool=solo
celery -A ai_trading_engine beat -l info
```

---

## Acceptance Criteria
- 100% coverage for 2020-01-01 → 2025-09-30 for chosen timeframes (at least 1h and 1d) across all supported symbols.
- Backtests never use synthetic data; services error clearly if data is missing.
- Monthly (and daily incremental) updates maintain ≥99% completeness.
- Data retention respects storage policy while preserving backtest reproducibility.

---

## Change Log
- v0.1: Initial phase plan and runbook created.
- v0.2: Implemented data model changes (MarketData.timeframe, HistoricalDataRange, DataQuality). Added migration steps.


