from django.core.management.base import BaseCommand
from apps.signals.services import SignalGenerationService
from apps.trading.models import Symbol
from apps.data.tasks import calculate_technical_indicators_task
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate trading signals for all active symbols'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of symbol codes to generate signals for',
        )
        parser.add_argument(
            '--update-indicators',
            action='store_true',
            help='Update technical indicators before generating signals',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting signal generation...')
        
        # Update technical indicators if requested
        if options['update_indicators']:
            self.stdout.write('Updating technical indicators...')
            calculate_technical_indicators_task()
            self.stdout.write('Technical indicators updated.')
        
        # Initialize signal generation service
        signal_service = SignalGenerationService()
        
        # Get symbols to process
        if options['symbols']:
            symbol_codes = [s.strip().upper() for s in options['symbols'].split(',')]
            symbols = Symbol.objects.filter(symbol__in=symbol_codes, is_active=True)
        else:
            symbols = Symbol.objects.filter(is_active=True)
        
        self.stdout.write(f'Processing {symbols.count()} symbols...')
        
        # Collect ALL signals from ALL symbols first
        all_signals = []
        processed_symbols = 0
        
        for symbol in symbols:
            try:
                signals = signal_service.generate_signals_for_symbol(symbol)
                all_signals.extend(signals)
                processed_symbols += 1
                
                if len(signals) > 0:
                    self.stdout.write(
                        f'  {symbol.symbol}: Generated {len(signals)} signals'
                    )
                else:
                    self.stdout.write(
                        f'  {symbol.symbol}: No signals generated'
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'[ERROR] {symbol.symbol}: Error - {str(e)}'
                    )
                )
                logger.error(f'Error generating signals for {symbol.symbol}: {e}')
        
        # Now select only the TOP 5 best signals globally
        self.stdout.write(f'\nCollected {len(all_signals)} total signals from {processed_symbols} symbols')
        
        if all_signals:
            # Archive old signals first before clearing them
            from apps.signals.models import TradingSignal, SignalHistory
            old_signals = TradingSignal.objects.filter(is_valid=True)
            old_signals_count = old_signals.count()
            
            if old_signals_count > 0:
                # Archive signals to history
                archived_count = 0
                for signal in old_signals:
                    try:
                        SignalHistory.objects.create(
                            symbol_name=signal.symbol.symbol,
                            signal_type_name=signal.signal_type.name,
                            strength=signal.strength,
                            confidence_score=signal.confidence_score,
                            confidence_level=signal.confidence_level,
                            entry_price=signal.entry_price,
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            risk_reward_ratio=signal.risk_reward_ratio,
                            timeframe=signal.timeframe,
                            entry_point_type=signal.entry_point_type,
                            entry_point_details=signal.entry_point_details,
                            entry_zone_low=signal.entry_zone_low,
                            entry_zone_high=signal.entry_zone_high,
                            entry_confidence=signal.entry_confidence,
                            quality_score=signal.quality_score,
                            is_valid=signal.is_valid,
                            expires_at=signal.expires_at,
                            technical_score=signal.technical_score,
                            sentiment_score=signal.sentiment_score,
                            news_score=signal.news_score,
                            volume_score=signal.volume_score,
                            pattern_score=signal.pattern_score,
                            economic_score=signal.economic_score,
                            sector_score=signal.sector_score,
                            is_executed=signal.is_executed,
                            executed_at=signal.executed_at,
                            execution_price=signal.execution_price,
                            is_profitable=signal.is_profitable,
                            profit_loss=signal.profit_loss,
                            original_signal_id=signal.id,
                            archived_reason='HOURLY_ROTATION',
                            notes=signal.notes
                        )
                        archived_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error archiving signal {signal.id}: {e}'))
                
                self.stdout.write(f'Archived {archived_count} old signals to history')
            
            # Clear old signals from active table
            TradingSignal.objects.filter(is_valid=True).delete()
            self.stdout.write(f'Cleared {old_signals_count} old signals from database')
            
            # Filter signals by quality first
            filtered_signals = signal_service._filter_signals_by_quality(all_signals)
            self.stdout.write(f'After quality filtering: {len(filtered_signals)} signals')
            
            # Select top 5 best signals globally
            top_5_signals = signal_service._select_top_signals(filtered_signals, 5)
            
            # Save only the top 5 signals to database
            saved_count = 0
            for signal in top_5_signals:
                try:
                    signal.save()
                    saved_count += 1
                    # Calculate accuracy score for display
                    accuracy_score = signal_service._calculate_accuracy_score(signal)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[TOP 5] {signal.symbol.symbol}: {signal.signal_type.name} - '
                            f'Confidence: {signal.confidence_score:.2f} - '
                            f'Accuracy: {accuracy_score:.2f}'
                        )
                    )
                except Exception as e:
                    logger.error(f'Error saving signal: {e}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSignal generation completed!\n'
                    f'Processed: {processed_symbols} symbols\n'
                    f'Collected: {len(all_signals)} total signals\n'
                    f'Quality filtered: {len(filtered_signals)} signals\n'
                    f'Selected top 5: {len(top_5_signals)} signals\n'
                    f'Saved to database: {saved_count} signals'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'\nNo signals generated from {processed_symbols} symbols'
                )
            )



