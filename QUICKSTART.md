# Quick Start Guide - AI-Enhanced Trading Signal Engine

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git

### 1. Clone and Setup
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd ai-trading-signal-engine

# Run the setup script
python setup.py
```

### 2. Manual Setup (Alternative)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup sample data
python manage.py setup_sample_data
```

### 3. Start the Application
```bash
# Start the development server
python manage.py runserver
```

### 4. Access the Application
- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Dashboard**: http://localhost:8000/dashboard/

### 5. Default Credentials
- **Username**: admin
- **Password**: admin123

## 📊 Features Overview

### Core Features
- ✅ **Portfolio Management**: Track positions and performance
- ✅ **AI Signal Generation**: Machine learning-powered trading signals
- ✅ **Risk Management**: Built-in position sizing and risk controls
- ✅ **Real-time Dashboard**: Live monitoring of trades and signals
- ✅ **Admin Interface**: Comprehensive admin panel for data management

### Technology Stack
- **Backend**: Django 4.2.7
- **Database**: SQLite (development) / MySQL (production)
- **Task Queue**: Celery with Redis
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5 + Chart.js

## 🗂️ Project Structure

```
ai_trading_engine/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── setup.py                 # Automated setup script
├── README.md               # Project documentation
├── QUICKSTART.md           # This file
├── ai_trading_engine/      # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── celery.py          # Celery configuration
│   └── wsgi.py            # WSGI application
├── apps/                   # Django applications
│   ├── core/              # Core functionality
│   ├── trading/           # Trading models and logic
│   ├── signals/           # AI signal generation
│   ├── data/              # Market data management
│   └── dashboard/         # Web dashboard
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS)
├── media/                # User uploaded files
└── logs/                 # Application logs
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
DEFAULT_CURRENCY=USD
RISK_PERCENTAGE=2.0
MAX_POSITION_SIZE=10.0
```

### Database Setup
For production, configure MySQL:

```sql
CREATE DATABASE ai_trading_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'trading_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ai_trading_engine.* TO 'trading_user'@'localhost';
FLUSH PRIVILEGES;
```

## 📈 Sample Data

The setup includes sample data:
- **Trading Symbols**: BTC, ETH, AAPL, GOOGL, TSLA, MSFT, AMZN, NVDA
- **AI Models**: LSTM Price Predictor, Ensemble Classifier, Transformer Signal Generator
- **Data Sources**: Yahoo Finance, Binance API, Alpha Vantage
- **Sample Portfolio**: Admin user with $10,000 balance

## 🚀 Development

### Running Tests
```bash
python manage.py test
```

### Creating New Models
```bash
python manage.py makemigrations
python manage.py migrate
```

### Adding Sample Data
```bash
python manage.py setup_sample_data
```

### Celery Tasks (Optional)
```bash
# Start Redis server
redis-server

# Start Celery worker
celery -A ai_trading_engine worker -l info
```

## 🔒 Security Notes

- Change default admin password in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Configure proper CORS settings
- Set DEBUG=False in production

## 📚 Next Steps

1. **Explore the Admin Panel**: Add more symbols, AI models, and data sources
2. **Customize Trading Logic**: Modify risk management settings
3. **Integrate Real Data**: Connect to live market data APIs
4. **Deploy to Production**: Set up MySQL, Redis, and proper hosting
5. **Add More Features**: Implement backtesting, advanced analytics, etc.

## 🆘 Troubleshooting

### Common Issues

**Port 8000 already in use:**
```bash
python manage.py runserver 8001
```

**Database errors:**
```bash
python manage.py migrate --run-syncdb
```

**Static files not loading:**
```bash
python manage.py collectstatic
```

**Import errors:**
```bash
pip install -r requirements.txt
```

## 📞 Support

- Check the main README.md for detailed documentation
- Review Django documentation for framework-specific questions
- Open an issue on GitHub for bugs or feature requests

---

**Happy Trading! 🚀📈**
