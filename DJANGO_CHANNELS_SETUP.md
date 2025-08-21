# Django Channels Setup - Real-Time Features

## Overview

This document describes the Django Channels implementation for real-time WebSocket features in the AI Trading Engine. The system provides live market data streaming, instant trading signals, and real-time notifications.

## Architecture

### Components

1. **ASGI Application** (`ai_trading_engine/asgi.py`)
   - Configures WebSocket routing alongside HTTP routing
   - Uses Daphne as the ASGI server

2. **WebSocket Consumers** (`apps/core/consumers.py`)
   - `MarketDataConsumer` - Handles real-time market data
   - `TradingSignalsConsumer` - Manages trading signal updates
   - `NotificationsConsumer` - Delivers user notifications

3. **Channel Routing** (`apps/core/routing.py`)
   - Maps WebSocket URLs to consumers
   - Supports multiple connection types

4. **Broadcasting Services** (`apps/core/services.py`)
   - `RealTimeBroadcaster` - Base broadcasting functionality
   - `MarketDataBroadcaster` - Specialized for market updates
   - `TradingSignalsBroadcaster` - Handles signal broadcasting
   - `NotificationBroadcaster` - Manages user notifications

5. **WebSocket Client** (`static/js/websocket_client.js`)
   - JavaScript client for browser connections
   - Auto-reconnection with exponential backoff
   - Event-driven message handling

## Setup Requirements

### Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `channels>=4.0.0` - Django Channels framework
- `channels-redis>=4.1.0` - Redis backend for channels
- `daphne>=4.0.0` - ASGI server
- `django-redis>=5.4.0` - Redis caching backend
- `redis>=4.6.0` - Redis Python client

### Redis Configuration

1. Install Redis server
2. Use the provided `redis.conf` configuration
3. Ensure Redis is running on `127.0.0.1:6379`

### Django Settings

The following settings are configured in `ai_trading_engine/settings.py`:

```python
# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# ASGI Application
ASGI_APPLICATION = 'ai_trading_engine.asgi.application'

# Redis Configuration
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Running the Application

### Development Server

```bash
# Run with Daphne (ASGI server)
daphne ai_trading_engine.asgi:application

# Or use Django's built-in ASGI support
python manage.py runserver
```

### Production Server

```bash
# Using Daphne
daphne -b 0.0.0.0 -p 8000 ai_trading_engine.asgi:application

# Using Gunicorn with ASGI worker
gunicorn ai_trading_engine.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
```

## WebSocket Endpoints

### Available Connections

1. **Market Data**: `/ws/market-data/`
   - Real-time price updates
   - Volume changes
   - Market movements

2. **Trading Signals**: `/ws/trading-signals/`
   - BUY/SELL/HOLD signals
   - Signal updates and modifications
   - Confidence score changes

3. **Notifications**: `/ws/notifications/`
   - User-specific alerts
   - Trade confirmations
   - Risk warnings
   - Portfolio updates

### Message Types

#### Market Updates
```json
{
    "type": "market_update",
    "symbol": "BTC-USD",
    "price": 45000.00,
    "change": 2.5,
    "volume": 1000000,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Trading Signals
```json
{
    "type": "new_signal",
    "signal_id": "signal_123",
    "symbol": "BTC-USD",
    "signal_type": "BUY",
    "strength": "STRONG",
    "confidence_score": 85,
    "entry_price": 45000.00,
    "target_price": 50000.00,
    "stop_loss": 42000.00,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Notifications
```json
{
    "type": "new_notification",
    "notification_id": "notif_456",
    "title": "Trade Executed",
    "message": "BUY 100 BTC-USD @ $45000",
    "notification_type": "trade",
    "priority": "high",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Testing

### WebSocket Test Page

Visit `/websocket-test/` to test WebSocket connections and broadcasting.

### Management Commands

```bash
# Test all WebSocket functionality
python manage.py test_websockets

# Test specific types
python manage.py test_websockets --type market --count 10 --delay 1.0
python manage.py test_websockets --type signals --count 5 --delay 2.0
python manage.py test_websockets --type notifications --count 3 --delay 1.5
```

### Manual Testing

1. Open the WebSocket test page
2. Connect to different WebSocket types
3. Run tests using the management command
4. Observe real-time updates in the browser

## Broadcasting Messages

### From Python Code

```python
from apps.core.services import market_broadcaster, signals_broadcaster

# Broadcast market update
market_broadcaster.broadcast_market_update(
    symbol="BTC-USD",
    price=45000.00,
    change=2.5,
    volume=1000000
)

# Broadcast trading signal
signals_broadcaster.broadcast_buy_signal(
    signal_id="signal_123",
    symbol="BTC-USD",
    entry_price=45000.00,
    target_price=50000.00,
    stop_loss=42000.00,
    confidence_score=85
)
```

### From JavaScript

```javascript
// Subscribe to symbol updates
window.websocketClient.subscribeToSymbol('BTC-USD');

// Filter trading signals
window.websocketClient.filterSignals('BTC-USD', 'BUY');

// Mark notification as read
window.websocketClient.markNotificationRead('notif_123');
```

## Error Handling

### Connection Failures

- Automatic reconnection with exponential backoff
- Maximum 5 reconnection attempts
- Graceful degradation to polling if WebSocket unavailable

### Message Validation

- JSON format validation
- Required field checking
- Error responses for invalid messages

### Logging

- Comprehensive logging for debugging
- Error tracking and monitoring
- Performance metrics collection

## Performance Considerations

### Redis Optimization

- Connection pooling
- Memory management (256MB limit)
- Efficient data structures

### WebSocket Management

- Group-based broadcasting for scalability
- Connection limits and monitoring
- Message queuing for high-volume scenarios

### Caching Strategy

- Redis-based caching for frequently accessed data
- Database query optimization
- Background task processing

## Security

### Authentication

- User authentication required for WebSocket connections
- Anonymous connections rejected
- User-specific message routing

### Data Validation

- Input sanitization
- CSRF protection for HTTP endpoints
- Rate limiting for API calls

### Access Control

- Symbol-specific subscriptions
- User permission checking
- Secure message routing

## Monitoring

### Connection Status

- Real-time connection monitoring
- User connection tracking
- Performance metrics collection

### Error Tracking

- WebSocket error logging
- Connection failure monitoring
- Performance degradation alerts

### Usage Analytics

- Message volume tracking
- User engagement metrics
- System performance monitoring

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check Redis server status
   - Verify connection settings
   - Check firewall configuration

2. **WebSocket Connection Refused**
   - Ensure ASGI server is running
   - Check URL routing configuration
   - Verify consumer implementation

3. **Messages Not Broadcasting**
   - Check channel layer configuration
   - Verify group membership
   - Review consumer logic

### Debug Commands

```bash
# Check Redis status
redis-cli ping

# Monitor Redis operations
redis-cli monitor

# Check Django channels
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> print(channel_layer)
```

## Future Enhancements

### Planned Features

1. **Message Persistence**
   - Store WebSocket messages in database
   - Message history and replay
   - Offline message queuing

2. **Advanced Routing**
   - Dynamic channel creation
   - Load balancing support
   - Geographic distribution

3. **Performance Optimization**
   - Message compression
   - Binary protocol support
   - Connection multiplexing

4. **Monitoring Dashboard**
   - Real-time connection visualization
   - Performance metrics display
   - Error tracking interface

## Support

For issues or questions regarding the Django Channels implementation:

1. Check the Django Channels documentation
2. Review the WebSocket test page
3. Use the management commands for testing
4. Check the application logs for errors
5. Verify Redis and ASGI server configuration








