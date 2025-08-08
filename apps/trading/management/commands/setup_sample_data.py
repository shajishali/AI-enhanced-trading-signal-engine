from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.trading.models import Portfolio, Symbol, RiskSettings
from apps.signals.models import SignalType, AIModel
from apps.data.models import DataSource
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up sample data for the AI Trading Engine'

    def handle(self, *args, **options):
        self.stdout.write('Setting up sample data...')
        
        # Create sample symbols
        symbols_data = [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'symbol_type': 'CRYPTO', 'exchange': 'Binance'},
            {'symbol': 'ETH', 'name': 'Ethereum', 'symbol_type': 'CRYPTO', 'exchange': 'Binance'},
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'symbol_type': 'STOCK', 'exchange': 'NASDAQ'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'symbol_type': 'STOCK', 'exchange': 'NASDAQ'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'symbol_type': 'STOCK', 'exchange': 'NASDAQ'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'symbol_type': 'STOCK', 'exchange': 'NASDAQ'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'symbol_type': 'STOCK', 'exchange': 'NASDAQ'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'symbol_type': 'STOCK', 'exchange': 'NASDAQ'},
        ]
        
        for symbol_data in symbols_data:
            symbol, created = Symbol.objects.get_or_create(
                symbol=symbol_data['symbol'],
                defaults=symbol_data
            )
            if created:
                self.stdout.write(f'Created symbol: {symbol.symbol}')
        
        # Create sample signal types
        signal_types_data = [
            {'name': 'Technical Analysis', 'description': 'Signals based on technical indicators'},
            {'name': 'Pattern Recognition', 'description': 'Signals based on chart patterns'},
            {'name': 'Machine Learning', 'description': 'AI-powered signal generation'},
            {'name': 'Sentiment Analysis', 'description': 'Signals based on market sentiment'},
        ]
        
        for signal_type_data in signal_types_data:
            signal_type, created = SignalType.objects.get_or_create(
                name=signal_type_data['name'],
                defaults=signal_type_data
            )
            if created:
                self.stdout.write(f'Created signal type: {signal_type.name}')
        
        # Create sample AI models
        ai_models_data = [
            {
                'name': 'LSTM Price Predictor',
                'model_type': 'LSTM',
                'version': '1.0',
                'description': 'Long Short-Term Memory model for price prediction',
                'accuracy': Decimal('85.5')
            },
            {
                'name': 'Ensemble Classifier',
                'model_type': 'ENSEMBLE',
                'version': '2.1',
                'description': 'Ensemble model combining multiple algorithms',
                'accuracy': Decimal('87.2')
            },
            {
                'name': 'Transformer Signal Generator',
                'model_type': 'TRANSFORMER',
                'version': '1.5',
                'description': 'Transformer-based model for signal generation',
                'accuracy': Decimal('89.1')
            },
        ]
        
        for model_data in ai_models_data:
            ai_model, created = AIModel.objects.get_or_create(
                name=model_data['name'],
                version=model_data['version'],
                defaults=model_data
            )
            if created:
                self.stdout.write(f'Created AI model: {ai_model.name}')
        
        # Create sample data sources
        data_sources_data = [
            {
                'name': 'Yahoo Finance',
                'source_type': 'API',
                'base_url': 'https://finance.yahoo.com',
                'api_key': ''
            },
            {
                'name': 'Binance API',
                'source_type': 'API',
                'base_url': 'https://api.binance.com',
                'api_key': ''
            },
            {
                'name': 'Alpha Vantage',
                'source_type': 'API',
                'base_url': 'https://www.alphavantage.co',
                'api_key': ''
            },
        ]
        
        for source_data in data_sources_data:
            data_source, created = DataSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            if created:
                self.stdout.write(f'Created data source: {data_source.name}')
        
        # Create portfolio for admin user
        admin_user = User.objects.get(username='admin')
        portfolio, created = Portfolio.objects.get_or_create(
            user=admin_user,
            defaults={
                'name': 'Main Portfolio',
                'balance': Decimal('10000.00'),
                'currency': 'USD'
            }
        )
        if created:
            self.stdout.write(f'Created portfolio for admin user')
        
        # Create risk settings for admin portfolio
        risk_settings, created = RiskSettings.objects.get_or_create(
            portfolio=portfolio,
            defaults={
                'max_position_size': Decimal('10.0'),
                'max_risk_per_trade': Decimal('2.0'),
                'stop_loss_percentage': Decimal('5.0'),
                'take_profit_percentage': Decimal('10.0')
            }
        )
        if created:
            self.stdout.write(f'Created risk settings for admin portfolio')
        
        self.stdout.write(
            self.style.SUCCESS('Sample data setup completed successfully!')
        )
