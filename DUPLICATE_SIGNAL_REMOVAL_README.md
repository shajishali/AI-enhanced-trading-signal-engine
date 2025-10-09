# Duplicate Signal Removal System

This system provides comprehensive tools for identifying and removing duplicate trading signals from the database. It addresses the issue where identical signals are generated for different dates but with the same core characteristics (symbol, signal type, prices, confidence levels, etc.).

## Problem Description

In the backtesting page, you may notice that some signals appear to be identical across different months/dates. For example:
- Same symbol (AAVEUSDT)
- Same signal type (SELL)
- Same confidence level (MODERATE 70%)
- Same prices ($820.32, $697.28, $885.95)
- Same risk-reward ratio (1.87)
- Same quality score (0.70)

These are considered duplicates because they represent the same trading opportunity, just generated at different times.

## Components

### 1. DuplicateSignalRemovalService (`apps/signals/duplicate_signal_removal_service.py`)

The core service that handles duplicate detection and removal logic.

**Key Features:**
- Identifies duplicates based on core signal characteristics
- Configurable price tolerance for grouping similar signals
- Keeps the earliest signal when removing duplicates
- Provides comprehensive statistics and reporting
- Supports dry-run mode for safe testing

**Main Methods:**
- `identify_duplicates()` - Find duplicate groups without removing them
- `remove_duplicates()` - Remove duplicates with optional dry-run mode
- `get_duplicate_statistics()` - Get comprehensive duplicate statistics
- `cleanup_old_duplicates()` - Remove duplicates older than specified days

### 2. Management Command (`apps/signals/management/commands/remove_duplicate_signals.py`)

Command-line interface for duplicate removal operations.

**Usage Examples:**
```bash
# Preview duplicates without removing them
python manage.py remove_duplicate_signals --dry-run

# Remove duplicates for a specific symbol
python manage.py remove_duplicate_signals --symbol AAVEUSDT --dry-run

# Remove duplicates with custom tolerance (2%)
python manage.py remove_duplicate_signals --tolerance 0.02 --dry-run

# Remove duplicates older than 30 days
python manage.py remove_duplicate_signals --cleanup-old --days-old 30 --dry-run

# Get statistics only
python manage.py remove_duplicate_signals --statistics-only

# Actually remove duplicates (remove --dry-run)
python manage.py remove_duplicate_signals --symbol AAVEUSDT
```

### 3. REST API (`apps/signals/duplicate_signal_api.py`)

Web API endpoints for duplicate signal management.

**Endpoints:**
- `GET /signals/api/duplicates/?action=statistics` - Get duplicate statistics
- `GET /signals/api/duplicates/?action=identify` - Identify duplicates
- `POST /signals/api/duplicates/` - Remove duplicates
- `GET /signals/api/duplicates/dashboard/` - Get dashboard data

### 4. Web Interface (`templates/signals/duplicate_signals.html`)

User-friendly web interface for duplicate signal management.

**Features:**
- Real-time statistics display
- Interactive duplicate identification
- Safe preview mode before removal
- Bulk cleanup of old duplicates
- Comprehensive reporting

## How Duplicate Detection Works

### Signal Grouping Criteria

Signals are considered duplicates if they have the same:

1. **Symbol** - Trading pair (e.g., AAVEUSDT)
2. **Signal Type** - BUY/SELL/HOLD
3. **Strength** - WEAK/MODERATE/STRONG/VERY_STRONG
4. **Confidence Level** - LOW/MEDIUM/HIGH/VERY_HIGH
5. **Prices** (within tolerance):
   - Entry price
   - Target price
   - Stop loss
6. **Risk-Reward Ratio** (rounded to 2 decimal places)
7. **Quality Score** (rounded to 2 decimal places)
8. **Timeframe** - 1M/5M/15M/1H/4H/1D/etc.
9. **Entry Point Type** - Pattern type that triggered the signal

### Price Tolerance

The system uses configurable price tolerance to group similar prices. For example:
- With 1% tolerance: $820.32 and $828.52 would be considered the same
- With 0.5% tolerance: Only $820.32 and $824.32 would be considered the same

### Duplicate Resolution

When duplicates are found:
1. All signals in the group are sorted by creation date (earliest first)
2. The earliest signal is kept
3. All other signals in the group are marked for removal
4. Removal is performed in a database transaction for safety

## Usage Instructions

### 1. Web Interface

1. Navigate to `/signals/duplicates/` in your browser
2. View current duplicate statistics
3. Use "Identify Duplicates" to find duplicates without removing them
4. Use "Remove Duplicates" with dry-run enabled to preview changes
5. Uncheck "Dry Run" and confirm to actually remove duplicates
6. Use "Cleanup Old Duplicates" to remove duplicates older than specified days

### 2. Command Line

```bash
# Always start with dry-run to preview changes
python manage.py remove_duplicate_signals --dry-run

# For specific symbol
python manage.py remove_duplicate_signals --symbol AAVEUSDT --dry-run

# With custom tolerance
python manage.py remove_duplicate_signals --tolerance 0.02 --dry-run

# For date range
python manage.py remove_duplicate_signals --start-date 2021-09-01 --end-date 2021-10-31 --dry-run

# Get statistics
python manage.py remove_duplicate_signals --statistics-only

# Cleanup old duplicates
python manage.py remove_duplicate_signals --cleanup-old --days-old 30 --dry-run

# Actually perform removal (remove --dry-run)
python manage.py remove_duplicate_signals --symbol AAVEUSDT
```

### 3. API Usage

```javascript
// Get statistics
fetch('/signals/api/duplicates/?action=statistics')
  .then(response => response.json())
  .then(data => console.log(data));

// Identify duplicates
fetch('/signals/api/duplicates/?action=identify&symbol=AAVEUSDT&tolerance=0.01')
  .then(response => response.json())
  .then(data => console.log(data));

// Remove duplicates (dry run)
fetch('/signals/api/duplicates/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    action: 'remove',
    symbol: 'AAVEUSDT',
    tolerance: 0.01,
    dry_run: true
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Safety Features

### 1. Dry Run Mode
- Always preview changes before actual removal
- Shows exactly what would be removed
- No database changes are made in dry-run mode

### 2. Transaction Safety
- All removals are performed in database transactions
- If an error occurs, all changes are rolled back
- Database integrity is maintained

### 3. Comprehensive Logging
- All operations are logged with detailed information
- Error handling with descriptive messages
- Audit trail of all duplicate removal operations

### 4. Backup Recommendations
Before running duplicate removal on production data:
```bash
# Create database backup
python manage.py dumpdata signals > signals_backup.json

# Or use your database backup tools
pg_dump your_database > backup.sql
```

## Configuration Options

### Tolerance Settings
- **0.005 (0.5%)** - Very strict, only exact matches
- **0.01 (1%)** - Default, good balance
- **0.02 (2%)** - More lenient, groups similar prices
- **0.05 (5%)** - Very lenient, may group different signals

### Time-based Filtering
- Filter by specific date ranges
- Cleanup old duplicates automatically
- Focus on recent duplicates for analysis

### Symbol Filtering
- Process specific trading pairs
- Analyze duplicates per symbol
- Targeted cleanup operations

## Monitoring and Reporting

### Statistics Provided
- Total signals in database
- Number of duplicate groups found
- Total duplicate signals
- Duplicate percentage
- Symbols with most duplicates
- Average time span between duplicates
- Signal types with duplicates

### Example Output
```
=== DUPLICATE STATISTICS ===
Total signals: 1,250
Total duplicates: 45
Duplicate percentage: 3.60%
Duplicate groups: 12
Symbols with duplicates: AAVEUSDT, BTCUSDT, ETHUSDT
Average duplicate time span: 24.5 hours
```

## Troubleshooting

### Common Issues

1. **No duplicates found**
   - Check if tolerance is too strict
   - Verify date range includes signals
   - Ensure symbol filter is correct

2. **Too many duplicates found**
   - Reduce tolerance percentage
   - Check if signals are actually different
   - Review grouping criteria

3. **Permission errors**
   - Ensure user has database write permissions
   - Check Django authentication
   - Verify API access rights

### Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger('apps.signals.duplicate_signal_removal_service').setLevel(logging.DEBUG)
```

## Best Practices

1. **Always use dry-run first** - Preview changes before applying them
2. **Start with small batches** - Test on specific symbols or date ranges
3. **Monitor statistics** - Track duplicate patterns over time
4. **Regular cleanup** - Schedule periodic duplicate removal
5. **Backup before removal** - Always have a recovery plan
6. **Review results** - Verify that removed signals were actually duplicates

## Integration with Backtesting

The duplicate removal system integrates seamlessly with the backtesting functionality:

1. **Before backtesting** - Remove existing duplicates to get clean results
2. **After signal generation** - Run duplicate detection on new signals
3. **Periodic maintenance** - Schedule regular duplicate cleanup
4. **Quality assurance** - Use duplicate statistics to monitor signal quality

## Future Enhancements

Potential improvements to consider:
- Machine learning-based duplicate detection
- Automatic duplicate prevention during signal generation
- Advanced similarity scoring algorithms
- Integration with signal quality metrics
- Real-time duplicate monitoring
- Custom duplicate detection rules per strategy

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Use the web interface for visual debugging
3. Run with `--statistics-only` to understand current state
4. Start with small test cases before full deployment
