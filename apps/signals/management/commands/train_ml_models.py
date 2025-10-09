from django.core.management.base import BaseCommand
from apps.signals.ml_model_training_service import MLModelTrainingService
from apps.signals.ml_integration_service import MLIntegrationService
from apps.signals.models import ChartMLModel, ChartMLPrediction
from apps.trading.models import Symbol
import logging
import json

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Train and manage ML models for chart-based signal generation (Phase 5.4)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['train', 'evaluate', 'predict', 'integrate', 'status'],
            default='train',
            help='Action to perform (default: train)',
        )
        parser.add_argument(
            '--model-name',
            type=str,
            help='Name for the model to train',
        )
        parser.add_argument(
            '--architecture',
            type=str,
            choices=['simple_cnn', 'resnet_like', 'attention_cnn', 'multi_task'],
            default='simple_cnn',
            help='Model architecture to use (default: simple_cnn)',
        )
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of symbol codes to train on',
        )
        parser.add_argument(
            '--model-id',
            type=int,
            help='Model ID for evaluation or prediction',
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=100,
            help='Number of training epochs (default: 100)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='Batch size for training (default: 32)',
        )
        parser.add_argument(
            '--learning-rate',
            type=float,
            default=0.001,
            help='Learning rate for training (default: 0.001)',
        )
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=0.7,
            help='Minimum confidence for training data (default: 0.7)',
        )
        parser.add_argument(
            '--balance-classes',
            action='store_true',
            help='Balance classes in training data',
        )
        parser.add_argument(
            '--augmentation',
            action='store_true',
            help='Use data augmentation during training',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting ML Model Training & Management (Phase 5.4)...')
        
        # Initialize services
        ml_training_service = MLModelTrainingService()
        ml_integration_service = MLIntegrationService()
        
        action = options['action']
        
        if action == 'train':
            self._train_model(ml_training_service, options)
        elif action == 'evaluate':
            self._evaluate_model(ml_training_service, options)
        elif action == 'predict':
            self._predict_with_model(ml_training_service, options)
        elif action == 'integrate':
            self._integrate_models(ml_integration_service, options)
        elif action == 'status':
            self._show_model_status(options)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown action: {action}'))
    
    def _train_model(self, ml_service, options):
        """Train a new ML model"""
        try:
            self.stdout.write('Training ML model...')
            
            # Get model name
            model_name = options['model_name']
            if not model_name:
                model_name = f"{options['architecture']}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get symbols
            symbols = None
            if options['symbols']:
                symbol_codes = [s.strip().upper() for s in options['symbols'].split(',')]
                symbols = Symbol.objects.filter(symbol__in=symbol_codes, is_active=True)
            
            self.stdout.write(f'Model name: {model_name}')
            self.stdout.write(f'Architecture: {options["architecture"]}')
            self.stdout.write(f'Epochs: {options["epochs"]}')
            self.stdout.write(f'Batch size: {options["batch_size"]}')
            self.stdout.write(f'Learning rate: {options["learning_rate"]}')
            
            # Update model configuration
            ml_service.model_config.update({
                'epochs': options['epochs'],
                'batch_size': options['batch_size'],
                'learning_rate': options['learning_rate']
            })
            
            ml_service.data_config.update({
                'min_confidence': options['min_confidence'],
                'balance_classes': options['balance_classes'],
                'augmentation': options['augmentation']
            })
            
            # Prepare training data
            self.stdout.write('Preparing training data...')
            data_result = ml_service.prepare_training_data(symbols)
            
            if data_result['status'] != 'success':
                self.stdout.write(self.style.ERROR(f'Error preparing training data: {data_result["message"]}'))
                return
            
            stats = data_result['stats']
            self.stdout.write(f'Training data prepared:')
            self.stdout.write(f'  Total charts: {stats["total_charts"]}')
            self.stdout.write(f'  Charts with entries: {stats["charts_with_entries"]}')
            self.stdout.write(f'  Charts with patterns: {stats["charts_with_patterns"]}')
            self.stdout.write(f'  Total entries: {stats["total_entries"]}')
            self.stdout.write(f'  Total patterns: {stats["total_patterns"]}')
            self.stdout.write(f'  Buy entries: {stats["buy_entries"]}')
            self.stdout.write(f'  Sell entries: {stats["sell_entries"]}')
            self.stdout.write(f'  Final samples: {stats["final_samples"]}')
            
            if stats['final_samples'] < 100:
                self.stdout.write(self.style.WARNING('Warning: Very few training samples. Consider lowering min_confidence.'))
            
            # Train model
            self.stdout.write('Starting model training...')
            training_result = ml_service.train_model(
                model_name=model_name,
                architecture=options['architecture'],
                training_data=data_result['data']
            )
            
            if training_result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Model {model_name} trained successfully!\n'
                        f'Model ID: {training_result["model_id"]}\n'
                        f'Accuracy: {training_result["accuracy"]:.4f}\n'
                        f'Model saved to: {training_result["model_path"]}'
                    )
                )
                
                # Display metrics
                metrics = training_result['metrics']
                self.stdout.write(f'\nModel Metrics:')
                self.stdout.write(f'  Test Accuracy: {metrics["test_accuracy"]:.4f}')
                self.stdout.write(f'  Test Loss: {metrics["test_loss"]:.4f}')
                
                if 'classification_report' in metrics:
                    report = metrics['classification_report']
                    self.stdout.write(f'  Precision: {report["macro avg"]["precision"]:.4f}')
                    self.stdout.write(f'  Recall: {report["macro avg"]["recall"]:.4f}')
                    self.stdout.write(f'  F1-Score: {report["macro avg"]["f1-score"]:.4f}')
            else:
                self.stdout.write(self.style.ERROR(f'Error training model: {training_result["message"]}'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in model training: {e}'))
    
    def _evaluate_model(self, ml_service, options):
        """Evaluate an existing model"""
        try:
            model_id = options['model_id']
            if not model_id:
                self.stdout.write(self.style.ERROR('Model ID is required for evaluation'))
                return
            
            self.stdout.write(f'Evaluating model {model_id}...')
            
            # Evaluate model
            evaluation_result = ml_service.evaluate_model(model_id)
            
            if evaluation_result['status'] == 'success':
                metrics = evaluation_result['metrics']
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Model {model_id} evaluation completed!\n'
                        f'Test Accuracy: {metrics["test_accuracy"]:.4f}\n'
                        f'Test Loss: {metrics["test_loss"]:.4f}'
                    )
                )
                
                # Display detailed metrics
                if 'classification_report' in metrics:
                    report = metrics['classification_report']
                    self.stdout.write(f'\nDetailed Metrics:')
                    self.stdout.write(f'  Precision: {report["macro avg"]["precision"]:.4f}')
                    self.stdout.write(f'  Recall: {report["macro avg"]["recall"]:.4f}')
                    self.stdout.write(f'  F1-Score: {report["macro avg"]["f1-score"]:.4f}')
                    
                    # Per-class metrics
                    self.stdout.write(f'\nPer-Class Metrics:')
                    for class_name, class_metrics in report.items():
                        if isinstance(class_metrics, dict) and 'precision' in class_metrics:
                            self.stdout.write(f'  {class_name}:')
                            self.stdout.write(f'    Precision: {class_metrics["precision"]:.4f}')
                            self.stdout.write(f'    Recall: {class_metrics["recall"]:.4f}')
                            self.stdout.write(f'    F1-Score: {class_metrics["f1-score"]:.4f}')
            else:
                self.stdout.write(self.style.ERROR(f'Error evaluating model: {evaluation_result["message"]}'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in model evaluation: {e}'))
    
    def _predict_with_model(self, ml_service, options):
        """Make predictions with a model"""
        try:
            model_id = options['model_id']
            if not model_id:
                self.stdout.write(self.style.ERROR('Model ID is required for prediction'))
                return
            
            self.stdout.write(f'Making predictions with model {model_id}...')
            
            # Get recent chart images
            from apps.signals.models import ChartImage
            recent_charts = ChartImage.objects.filter(
                is_training_data=True
            ).order_by('-created_at')[:5]
            
            if not recent_charts.exists():
                self.stdout.write(self.style.WARNING('No chart images found for prediction'))
                return
            
            predictions_made = 0
            
            for chart_image in recent_charts:
                try:
                    # Make prediction
                    prediction = ml_service.predict_entry_points(chart_image, model_id)
                    
                    if prediction['status'] == 'success':
                        predictions_made += 1
                        self.stdout.write(
                            f'Chart {chart_image.id} ({chart_image.symbol.symbol} - {chart_image.timeframe}): '
                            f'{prediction["entry_type"]} (confidence: {prediction["confidence"]:.4f})'
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to predict for chart {chart_image.id}: {prediction["message"]}')
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error predicting for chart {chart_image.id}: {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Completed {predictions_made} predictions with model {model_id}')
            )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in model prediction: {e}'))
    
    def _integrate_models(self, ml_integration_service, options):
        """Integrate ML models with signal generation"""
        try:
            self.stdout.write('Integrating ML models with signal generation...')
            
            # Get active models
            active_models = ChartMLModel.objects.filter(
                is_active=True,
                status='TRAINED'
            )
            
            if not active_models.exists():
                self.stdout.write(self.style.WARNING('No active ML models found for integration'))
                return
            
            self.stdout.write(f'Found {active_models.count()} active models')
            
            # Get symbols to test integration
            symbols = Symbol.objects.filter(is_active=True)[:3]
            
            integration_results = []
            
            for symbol in symbols:
                try:
                    self.stdout.write(f'Testing ML integration for {symbol.symbol}...')
                    
                    # Generate ML-enhanced signals
                    ml_signals = ml_integration_service.generate_ml_enhanced_signals(symbol)
                    
                    if ml_signals:
                        integration_results.append({
                            'symbol': symbol.symbol,
                            'signals_generated': len(ml_signals),
                            'avg_confidence': sum(s.confidence_score for s in ml_signals) / len(ml_signals),
                            'ml_enhanced_count': sum(1 for s in ml_signals if s.metadata and s.metadata.get('ml_enhanced', False))
                        })
                        
                        self.stdout.write(
                            f'  Generated {len(ml_signals)} signals (avg confidence: {integration_results[-1]["avg_confidence"]:.4f})'
                        )
                    else:
                        self.stdout.write(f'  No signals generated for {symbol.symbol}')
                
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error integrating for {symbol.symbol}: {e}')
                    )
            
            # Display integration summary
            if integration_results:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nML Integration Summary:\n'
                        f'Symbols tested: {len(integration_results)}\n'
                        f'Total signals: {sum(r["signals_generated"] for r in integration_results)}\n'
                        f'ML-enhanced signals: {sum(r["ml_enhanced_count"] for r in integration_results)}\n'
                        f'Average confidence: {sum(r["avg_confidence"] for r in integration_results) / len(integration_results):.4f}'
                    )
                )
            else:
                self.stdout.write(self.style.WARNING('No integration results to display'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in ML integration: {e}'))
    
    def _show_model_status(self, options):
        """Show status of all ML models"""
        try:
            self.stdout.write('ML Model Status Report')
            self.stdout.write('=' * 50)
            
            # Get all models
            models = ChartMLModel.objects.all().order_by('-created_at')
            
            if not models.exists():
                self.stdout.write('No ML models found')
                return
            
            for model in models:
                status_color = 'green' if model.status == 'TRAINED' else 'red' if model.status == 'FAILED' else 'yellow'
                status_text = self.style.SUCCESS(model.status) if model.status == 'TRAINED' else self.style.ERROR(model.status) if model.status == 'FAILED' else self.style.WARNING(model.status)
                
                self.stdout.write(f'\nModel: {model.name}')
                self.stdout.write(f'  ID: {model.id}')
                self.stdout.write(f'  Type: {model.model_type}')
                self.stdout.write(f'  Version: {model.version}')
                self.stdout.write(f'  Status: {status_text}')
                self.stdout.write(f'  Active: {"Yes" if model.is_active else "No"}')
                
                if model.accuracy_score:
                    self.stdout.write(f'  Accuracy: {model.accuracy_score:.4f}')
                if model.precision_score:
                    self.stdout.write(f'  Precision: {model.precision_score:.4f}')
                if model.recall_score:
                    self.stdout.write(f'  Recall: {model.recall_score:.4f}')
                if model.f1_score:
                    self.stdout.write(f'  F1-Score: {model.f1_score:.4f}')
                
                self.stdout.write(f'  Training Data Size: {model.training_data_size}')
                self.stdout.write(f'  Created: {model.created_at}')
                
                if model.last_evaluated_at:
                    self.stdout.write(f'  Last Evaluated: {model.last_evaluated_at}')
                
                # Get prediction count
                prediction_count = ChartMLPrediction.objects.filter(model=model).count()
                self.stdout.write(f'  Predictions Made: {prediction_count}')
            
            # Summary statistics
            trained_models = models.filter(status='TRAINED')
            active_models = models.filter(is_active=True)
            
            self.stdout.write(f'\nSummary:')
            self.stdout.write(f'  Total Models: {models.count()}')
            self.stdout.write(f'  Trained Models: {trained_models.count()}')
            self.stdout.write(f'  Active Models: {active_models.count()}')
            
            if trained_models.exists():
                avg_accuracy = sum(m.accuracy_score for m in trained_models if m.accuracy_score) / trained_models.count()
                self.stdout.write(f'  Average Accuracy: {avg_accuracy:.4f}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error showing model status: {e}'))

