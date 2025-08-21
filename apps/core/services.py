"""
Real-time broadcasting services for Django Channels
Handles sending messages to WebSocket consumers
"""

import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class RealTimeBroadcaster:
    """Service for broadcasting real-time messages to WebSocket consumers"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def broadcast_market_update(self, symbol, price, change, volume, timestamp=None):
        """Broadcast market data update to all connected clients"""
        if timestamp is None:
            timestamp = timezone.now()
        
        message = {
            'type': 'market_update',
            'symbol': symbol,
            'price': price,
            'change': change,
            'volume': volume,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'market_data',
                message
            )
            
            # Also send to symbol-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'market_data_{symbol}',
                message
            )
            
            logger.info(f"Broadcasted market update for {symbol}: ${price}")
            
        except Exception as e:
            logger.error(f"Error broadcasting market update for {symbol}: {e}")
    
    def broadcast_price_alert(self, symbol, alert_type, price, message, timestamp=None):
        """Broadcast price alert to all connected clients"""
        if timestamp is None:
            timestamp = timezone.now()
        
        alert_data = {
            'type': 'price_alert',
            'symbol': symbol,
            'alert_type': alert_type,
            'price': price,
            'message': message,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'market_data',
                alert_data
            )
            
            # Also send to symbol-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'market_data_{symbol}',
                alert_data
            )
            
            logger.info(f"Broadcasted price alert for {symbol}: {message}")
            
        except Exception as e:
            logger.error(f"Error broadcasting price alert for {symbol}: {e}")
    
    def broadcast_trading_signal(self, signal_id, symbol, signal_type, strength, 
                                confidence_score, entry_price, target_price, 
                                stop_loss, timestamp=None):
        """Broadcast new trading signal to all connected clients"""
        if timestamp is None:
            timestamp = timezone.now()
        
        signal_data = {
            'type': 'new_signal',
            'signal_id': signal_id,
            'symbol': symbol,
            'signal_type': signal_type,
            'strength': strength,
            'confidence_score': confidence_score,
            'entry_price': entry_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'trading_signals',
                signal_data
            )
            
            # Also send to symbol-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'signals_{symbol}',
                signal_data
            )
            
            logger.info(f"Broadcasted trading signal for {symbol}: {signal_type}")
            
        except Exception as e:
            logger.error(f"Error broadcasting trading signal for {symbol}: {e}")
    
    def broadcast_signal_update(self, signal_id, update_type, new_value, timestamp=None):
        """Broadcast signal update to all connected clients"""
        if timestamp is None:
            timestamp = timezone.now()
        
        update_data = {
            'type': 'signal_update',
            'signal_id': signal_id,
            'update_type': update_type,
            'new_value': new_value,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'trading_signals',
                update_data
            )
            
            logger.info(f"Broadcasted signal update for {signal_id}: {update_type}")
            
        except Exception as e:
            logger.error(f"Error broadcasting signal update for {signal_id}: {e}")
    
    def broadcast_notification(self, user_id, notification_id, title, message, 
                              notification_type, priority, timestamp=None):
        """Broadcast notification to specific user"""
        if timestamp is None:
            timestamp = timezone.now()
        
        notification_data = {
            'type': 'new_notification',
            'notification_id': notification_id,
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'priority': priority,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'notifications_{user_id}',
                notification_data
            )
            
            logger.info(f"Broadcasted notification to user {user_id}: {title}")
            
        except Exception as e:
            logger.error(f"Error broadcasting notification to user {user_id}: {e}")
    
    def broadcast_portfolio_update(self, user_id, total_value, daily_change, 
                                 daily_change_percent, timestamp=None):
        """Broadcast portfolio update to specific user"""
        if timestamp is None:
            timestamp = timezone.now()
        
        portfolio_data = {
            'type': 'portfolio_update',
            'total_value': total_value,
            'daily_change': daily_change,
            'daily_change_percent': daily_change_percent,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'notifications_{user_id}',
                portfolio_data
            )
            
            logger.info(f"Broadcasted portfolio update to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting portfolio update to user {user_id}: {e}")
    
    def broadcast_to_all_users(self, message_type, data):
        """Broadcast message to all connected users"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'all_users',
                {
                    'type': message_type,
                    **data
                }
            )
            
            logger.info(f"Broadcasted {message_type} to all users")
            
        except Exception as e:
            logger.error(f"Error broadcasting {message_type} to all users: {e}")
    
    def broadcast_to_group(self, group_name, message_type, data):
        """Broadcast message to specific group"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': message_type,
                    **data
                }
            )
            
            logger.info(f"Broadcasted {message_type} to group {group_name}")
            
        except Exception as e:
            logger.error(f"Error broadcasting {message_type} to group {group_name}: {e}")


class MarketDataBroadcaster(RealTimeBroadcaster):
    """Specialized broadcaster for market data updates"""
    
    def broadcast_crypto_update(self, symbol, price, change_24h, volume_24h, 
                               market_cap, timestamp=None):
        """Broadcast cryptocurrency market update"""
        if timestamp is None:
            timestamp = timezone.now()
        
        crypto_data = {
            'type': 'crypto_update',
            'symbol': symbol,
            'price': price,
            'change_24h': change_24h,
            'volume_24h': volume_24h,
            'market_cap': market_cap,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'market_data',
                crypto_data
            )
            
            # Also send to symbol-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'market_data_{symbol}',
                crypto_data
            )
            
            logger.info(f"Broadcasted crypto update for {symbol}: ${price}")
            
        except Exception as e:
            logger.error(f"Error broadcasting crypto update for {symbol}: {e}")
    
    def broadcast_stock_update(self, symbol, price, change, change_percent, 
                              volume, market_cap, pe_ratio, timestamp=None):
        """Broadcast stock market update"""
        if timestamp is None:
            timestamp = timezone.now()
        
        stock_data = {
            'type': 'stock_update',
            'symbol': symbol,
            'price': price,
            'change': change,
            'change_percent': change_percent,
            'volume': volume,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'market_data',
                stock_data
            )
            
            # Also send to symbol-specific group
            async_to_sync(self.channel_layer.group_send)(
                f'market_data_{symbol}',
                stock_data
            )
            
            logger.info(f"Broadcasted stock update for {symbol}: ${price}")
            
        except Exception as e:
            logger.error(f"Error broadcasting stock update for {symbol}: {e}")


class TradingSignalsBroadcaster(RealTimeBroadcaster):
    """Specialized broadcaster for trading signals"""
    
    def broadcast_buy_signal(self, signal_id, symbol, entry_price, target_price, 
                             stop_loss, confidence_score, timestamp=None):
        """Broadcast buy signal"""
        self.broadcast_trading_signal(
            signal_id=signal_id,
            symbol=symbol,
            signal_type='BUY',
            strength='STRONG',
            confidence_score=confidence_score,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            timestamp=timestamp
        )
    
    def broadcast_sell_signal(self, signal_id, symbol, entry_price, target_price, 
                              stop_loss, confidence_score, timestamp=None):
        """Broadcast sell signal"""
        self.broadcast_trading_signal(
            signal_id=signal_id,
            symbol=symbol,
            signal_type='SELL',
            strength='STRONG',
            confidence_score=confidence_score,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            timestamp=timestamp
        )
    
    def broadcast_hold_signal(self, signal_id, symbol, reason, confidence_score, timestamp=None):
        """Broadcast hold signal"""
        if timestamp is None:
            timestamp = timezone.now()
        
        hold_data = {
            'type': 'hold_signal',
            'signal_id': signal_id,
            'symbol': symbol,
            'signal_type': 'HOLD',
            'reason': reason,
            'confidence_score': confidence_score,
            'timestamp': timestamp.isoformat()
        }
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                'trading_signals',
                hold_data
            )
            
            logger.info(f"Broadcasted hold signal for {symbol}: {reason}")
            
        except Exception as e:
            logger.error(f"Error broadcasting hold signal for {symbol}: {e}")


class NotificationBroadcaster(RealTimeBroadcaster):
    """Specialized broadcaster for user notifications"""
    
    def broadcast_system_alert(self, user_id, title, message, priority='medium', timestamp=None):
        """Broadcast system alert to user"""
        self.broadcast_notification(
            user_id=user_id,
            notification_id=f"sys_{int(timezone.now().timestamp())}",
            title=title,
            message=message,
            notification_type='system',
            priority=priority,
            timestamp=timestamp
        )
    
    def broadcast_trade_notification(self, user_id, trade_type, symbol, quantity, 
                                    price, timestamp=None):
        """Broadcast trade execution notification"""
        title = f"Trade Executed: {trade_type.upper()}"
        message = f"{trade_type.title()} {quantity} {symbol} @ ${price}"
        
        self.broadcast_notification(
            user_id=user_id,
            notification_id=f"trade_{int(timezone.now().timestamp())}",
            title=title,
            message=message,
            notification_type='trade',
            priority='high',
            timestamp=timestamp
        )
    
    def broadcast_risk_alert(self, user_id, symbol, risk_level, message, timestamp=None):
        """Broadcast risk management alert"""
        title = f"Risk Alert: {symbol}"
        
        self.broadcast_notification(
            user_id=user_id,
            notification_id=f"risk_{int(timezone.now().timestamp())}",
            title=title,
            message=message,
            notification_type='risk',
            priority='high',
            timestamp=timestamp
        )


# Global broadcaster instances
market_broadcaster = MarketDataBroadcaster()
signals_broadcaster = TradingSignalsBroadcaster()
notification_broadcaster = NotificationBroadcaster()


