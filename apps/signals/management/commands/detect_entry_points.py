from django.core.management.base import BaseCommand
from apps.signals.multi_timeframe_entry_detection_service import MultiTimeframeEntryDetectionService
from apps.signals.models import ChartImage, EntryPoint
from apps.trading.models import Symbol
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Detect multi-timeframe entry points using SMC strategy (Phase 5.3)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of symbol codes to detect entry points for',
        )
        parser.add_argument(
            '--timeframes',
            type=str,
            default='1H,4H,1D',
            help='Comma-separated list of timeframes (default: 1H,4H,1D)',
        )
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=0.7,
            help='Minimum confidence score for entry points (default: 0.7)',
        )
        parser.add_argument(
            '--min-risk-reward',
            type=float,
            default=1.5,
            help='Minimum risk-reward ratio (default: 1.5)',
        )
        parser.add_argument(
            '--charts-limit',
            type=int,
            default=50,
            help='Maximum number of charts to process per symbol (default: 50)',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing entry points before detection',
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate existing entry points',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting multi-timeframe entry point detection (Phase 5.3)...')
        
        # Initialize multi-timeframe entry detection service
        entry_service = MultiTimeframeEntryDetectionService()
        
        # Get symbols to process
        if options['symbols']:
            symbol_codes = [s.strip().upper() for s in options['symbols'].split(',')]
            symbols = Symbol.objects.filter(symbol__in=symbol_codes, is_active=True)
        else:
            symbols = Symbol.objects.filter(is_active=True)[:5]  # Default to first 5
        
        timeframes = options['timeframes'].split(',')
        
        self.stdout.write(f'Processing {symbols.count()} symbols...')
        self.stdout.write(f'Timeframes: {", ".join(timeframes)}')
        self.stdout.write(f'Min confidence: {options["min_confidence"]}')
        self.stdout.write(f'Min risk-reward: {options["min_risk_reward"]}')
        
        # Clear existing entry points if requested
        if options['clear_existing']:
            self.stdout.write('Clearing existing entry points...')
            EntryPoint.objects.all().delete()
            self.stdout.write('Existing entry points cleared.')
        
        total_stats = {
            'symbols_processed': 0,
            'charts_processed': 0,
            'entry_points_detected': 0,
            'entry_points_saved': 0,
            'buy_entries': 0,
            'sell_entries': 0,
            'high_confidence': 0,
            'validated_entries': 0
        }
        
        for symbol in symbols:
            try:
                total_stats['symbols_processed'] += 1
                self.stdout.write(f'\n=== Processing {symbol.symbol} ===')
                
                symbol_stats = {
                    'charts_processed': 0,
                    'entry_points_detected': 0,
                    'entry_points_saved': 0,
                    'buy_entries': 0,
                    'sell_entries': 0,
                    'high_confidence': 0
                }
                
                if options['validate_only']:
                    # Only validate existing entry points
                    existing_entries = EntryPoint.objects.filter(
                        chart_image__symbol=symbol
                    )
                    
                    if existing_entries.exists():
                        validated_count = self._validate_existing_entries(
                            existing_entries, entry_service, options
                        )
                        symbol_stats['validated_entries'] = validated_count
                        self.stdout.write(f'  Validated {validated_count} existing entry points')
                    else:
                        self.stdout.write(f'  No existing entry points found for {symbol.symbol}')
                else:
                    # Detect new entry points
                    for timeframe in timeframes:
                        timeframe = timeframe.strip()
                        
                        # Get chart images for this symbol and timeframe
                        chart_images = ChartImage.objects.filter(
                            symbol=symbol,
                            timeframe=timeframe,
                            is_training_data=True
                        ).order_by('-created_at')[:options['charts_limit']]
                        
                        if not chart_images.exists():
                            self.stdout.write(f'  No charts found for {symbol.symbol} - {timeframe}')
                            continue
                        
                        self.stdout.write(f'  Processing {chart_images.count()} charts for {timeframe}...')
                        
                        for chart_image in chart_images:
                            try:
                                # Detect entry points for this chart
                                entry_points = entry_service.detect_entry_points_for_chart(chart_image)
                                
                                if entry_points:
                                    symbol_stats['charts_processed'] += 1
                                    
                                    # Filter entry points by criteria
                                    filtered_entries = self._filter_entry_points(
                                        entry_points, options
                                    )
                                    
                                    if filtered_entries:
                                        symbol_stats['entry_points_detected'] += len(filtered_entries)
                                        
                                        # Save entry points to database
                                        saved_count = self._save_entry_points(filtered_entries)
                                        symbol_stats['entry_points_saved'] += saved_count
                                        
                                        # Count by type and confidence
                                        for entry_point in filtered_entries:
                                            if entry_point.entry_type in ['BUY', 'BUY_LIMIT', 'BUY_STOP']:
                                                symbol_stats['buy_entries'] += 1
                                            elif entry_point.entry_type in ['SELL', 'SELL_LIMIT', 'SELL_STOP']:
                                                symbol_stats['sell_entries'] += 1
                                            
                                            if entry_point.confidence_score >= 0.8:
                                                symbol_stats['high_confidence'] += 1
                                        
                                        self.stdout.write(
                                            f'    ✓ Chart {chart_image.id}: {saved_count} entry points saved'
                                        )
                                
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f'    ✗ Error processing chart {chart_image.id}: {e}'
                                    )
                                )
                    
                    # Also detect entry points using multi-timeframe analysis
                    try:
                        multi_timeframe_entries = entry_service.detect_entry_points_for_symbol(symbol)
                        
                        if multi_timeframe_entries:
                            # Filter and save multi-timeframe entries
                            filtered_mtf_entries = self._filter_entry_points(
                                multi_timeframe_entries, options
                            )
                            
                            if filtered_mtf_entries:
                                saved_count = self._save_entry_points(filtered_mtf_entries)
                                symbol_stats['entry_points_saved'] += saved_count
                                symbol_stats['entry_points_detected'] += len(filtered_mtf_entries)
                                
                                self.stdout.write(
                                    f'  Multi-timeframe analysis: {saved_count} entry points saved'
                                )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  Error in multi-timeframe analysis: {e}')
                        )
                
                # Display symbol summary
                if symbol_stats['charts_processed'] > 0 or symbol_stats['entry_points_saved'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {symbol.symbol} completed: '
                            f'{symbol_stats["charts_processed"]} charts, '
                            f'{symbol_stats["entry_points_detected"]} entry points detected, '
                            f'{symbol_stats["entry_points_saved"]} entry points saved'
                        )
                    )
                    
                    # Display entry breakdown
                    if symbol_stats['buy_entries'] > 0:
                        self.stdout.write(f'    Buy entries: {symbol_stats["buy_entries"]}')
                    if symbol_stats['sell_entries'] > 0:
                        self.stdout.write(f'    Sell entries: {symbol_stats["sell_entries"]}')
                    if symbol_stats['high_confidence'] > 0:
                        self.stdout.write(f'    High confidence: {symbol_stats["high_confidence"]}')
                
                # Update total stats
                for key in symbol_stats:
                    if key in total_stats:
                        total_stats[key] += symbol_stats[key]
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing symbol {symbol.symbol}: {e}')
                )
        
        # Display final summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nMulti-Timeframe Entry Point Detection Completed!\n'
                f'Symbols processed: {total_stats["symbols_processed"]}\n'
                f'Charts processed: {total_stats["charts_processed"]}\n'
                f'Entry points detected: {total_stats["entry_points_detected"]}\n'
                f'Entry points saved: {total_stats["entry_points_saved"]}\n'
                f'\nEntry Breakdown:\n'
                f'  Buy entries: {total_stats["buy_entries"]}\n'
                f'  Sell entries: {total_stats["sell_entries"]}\n'
                f'  High confidence: {total_stats["high_confidence"]}'
            )
        )
    
    def _filter_entry_points(self, entry_points, options):
        """Filter entry points based on criteria"""
        filtered = []
        
        for entry_point in entry_points:
            # Check minimum confidence
            if entry_point.confidence_score < options['min_confidence']:
                continue
            
            # Check minimum risk-reward ratio
            if entry_point.risk_reward_ratio and entry_point.risk_reward_ratio < options['min_risk_reward']:
                continue
            
            filtered.append(entry_point)
        
        return filtered
    
    def _save_entry_points(self, entry_points):
        """Save entry points to database"""
        try:
            saved_count = 0
            
            for entry_point in entry_points:
                try:
                    entry_point.save()
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Error saving entry point: {e}")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving entry points: {e}")
            return 0
    
    def _validate_existing_entries(self, existing_entries, entry_service, options):
        """Validate existing entry points"""
        try:
            validated_count = 0
            
            for entry_point in existing_entries:
                try:
                    # Re-validate entry point
                    if entry_point.chart_image:
                        # Get fresh market data and indicators
                        market_data = entry_service._get_market_data_for_chart(entry_point.chart_image)
                        indicators = entry_service._get_technical_indicators(
                            entry_point.chart_image.symbol, 
                            entry_point.chart_image.timeframe
                        )
                        
                        if market_data and indicators:
                            # Check if entry is still valid
                            confirmation = entry_service._check_entry_confirmation_from_indicators(
                                indicators, entry_point.entry_type
                            )
                            
                            if confirmation['confirmed']:
                                # Update confidence score
                                entry_point.confidence_score = confirmation['confidence']
                                entry_point.is_validated = True
                                entry_point.save()
                                validated_count += 1
                            else:
                                # Mark as invalid
                                entry_point.is_validated = False
                                entry_point.save()
                
                except Exception as e:
                    logger.error(f"Error validating entry point {entry_point.id}: {e}")
            
            return validated_count
            
        except Exception as e:
            logger.error(f"Error validating existing entries: {e}")
            return 0

