from django.core.management.base import BaseCommand
from apps.signals.chart_image_generation_service import ChartImageGenerationService
from apps.trading.models import Symbol
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate chart images for ML training (Phase 5.1)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of symbol codes to generate charts for',
        )
        parser.add_argument(
            '--timeframes',
            type=str,
            default='1H,4H,1D',
            help='Comma-separated list of timeframes (default: 1H,4H,1D)',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Number of days back to generate charts (default: 30)',
        )
        parser.add_argument(
            '--training-dataset',
            action='store_true',
            help='Generate training dataset for all active symbols',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting chart image generation (Phase 5.1)...')
        
        # Initialize chart generation service
        chart_service = ChartImageGenerationService()
        
        if options['training_dataset']:
            # Generate training dataset for all active symbols
            symbols = Symbol.objects.filter(is_active=True)
            timeframes = options['timeframes'].split(',')
            
            self.stdout.write(f'Generating training dataset for {symbols.count()} symbols...')
            
            stats = chart_service.generate_training_dataset(
                symbols=list(symbols),
                timeframes=timeframes,
                days_back=options['days_back']
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Training dataset generation completed!\n'
                    f'Symbols processed: {stats["symbols_processed"]}\n'
                    f'Timeframes processed: {stats["timeframes_processed"]}\n'
                    f'Charts generated: {stats["total_generated"]}\n'
                    f'Failed: {stats["failed"]}'
                )
            )
            
        else:
            # Generate charts for specific symbols
            if options['symbols']:
                symbol_codes = [s.strip().upper() for s in options['symbols'].split(',')]
                symbols = Symbol.objects.filter(symbol__in=symbol_codes, is_active=True)
            else:
                symbols = Symbol.objects.filter(is_active=True)[:5]  # Default to first 5
            
            timeframes = options['timeframes'].split(',')
            
            self.stdout.write(f'Generating charts for {symbols.count()} symbols...')
            
            total_generated = 0
            total_failed = 0
            
            for symbol in symbols:
                for timeframe in timeframes:
                    try:
                        chart_image = chart_service.generate_chart_image(
                            symbol=symbol,
                            timeframe=timeframe.strip(),
                            chart_type='CANDLESTICK',
                            include_patterns=True,
                            include_entry_points=True
                        )
                        
                        if chart_image:
                            total_generated += 1
                            self.stdout.write(
                                f'  ✓ Generated chart for {symbol.symbol} - {timeframe}'
                            )
                        else:
                            total_failed += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  ✗ Failed to generate chart for {symbol.symbol} - {timeframe}'
                                )
                            )
                            
                    except Exception as e:
                        total_failed += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ Error generating chart for {symbol.symbol} - {timeframe}: {e}'
                            )
                        )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nChart generation completed!\n'
                    f'Charts generated: {total_generated}\n'
                    f'Failed: {total_failed}'
                )
            )

