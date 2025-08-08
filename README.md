# AI-Enhanced Trading Signal Engine

A sophisticated Django-based trading signal engine that leverages artificial intelligence to generate trading signals for various financial instruments.

## Features

- **Real-time Data Processing**: Integrates with multiple data sources for live market data
- **AI-Powered Signal Generation**: Machine learning models for pattern recognition and signal generation
- **Multi-Exchange Support**: Support for Binance, Coinbase, and other major exchanges
- **Interactive Dashboard**: Real-time visualization of signals and market data
- **Backtesting Engine**: Historical performance analysis of trading strategies
- **Risk Management**: Built-in position sizing and risk controls
- **RESTful API**: Comprehensive API for external integrations

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL 8.0
- **AI/ML**: scikit-learn, pandas, numpy
- **Data Sources**: yfinance, ccxt, python-binance
- **Visualization**: Plotly, Dash, matplotlib
- **Task Queue**: Celery with Redis
- **API**: Django REST Framework

## Project Structure

```
ai_trading_engine/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ai_trading_engine/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/
│   ├── trading/
│   ├── signals/
│   ├── data/
│   └── dashboard/
├── static/
├── templates/
├── media/
└── docs/
```

## Installation

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Redis (for Celery)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-trading-signal-engine
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up MySQL database**
   ```sql
   CREATE DATABASE ai_trading_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'trading_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON ai_trading_engine.* TO 'trading_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start Redis server**
   ```bash
   redis-server
   ```

9. **Start Celery worker**
   ```bash
   celery -A ai_trading_engine worker -l info
   ```

10. **Run the development server**
    ```bash
    python manage.py runserver
    ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://trading_user:password@localhost:3306/ai_trading_engine
REDIS_URL=redis://localhost:6379/0

# API Keys (optional for development)
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key
COINBASE_API_KEY=your-coinbase-api-key
COINBASE_SECRET_KEY=your-coinbase-secret-key
```

## Usage

### Accessing the Application

- **Main Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/

### Key Features

1. **Signal Generation**: AI models analyze market data to generate trading signals
2. **Portfolio Management**: Track positions and performance
3. **Risk Management**: Set stop-loss and take-profit levels
4. **Backtesting**: Test strategies on historical data
5. **Real-time Monitoring**: Live dashboard with market data and signals

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black .

# Check code quality
flake8 .

# Sort imports
isort .
```

## Deployment

### Production Setup

1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure Celery for production
5. Set up monitoring and logging

### Docker Deployment

```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.
