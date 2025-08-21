from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
import logging

from .services import market_broadcaster, signals_broadcaster, notification_broadcaster

logger = logging.getLogger(__name__)

# Create your views here.

# Custom error handlers for Phase 5
def handler404(request, exception):
    """Custom 404 error handler"""
    logger.warning(f"404 error for URL: {request.path}")
    return render(request, 'core/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    logger.error(f"500 error for URL: {request.path}")
    return render(request, 'core/500.html', status=500)

def handler403(request, exception):
    """Custom 403 error handler"""
    logger.warning(f"403 error for URL: {request.path}")
    return render(request, 'core/403.html', status=403)


@method_decorator(login_required, name='dispatch')
class PerformanceMetricsView(View):
    """View for performance metrics"""
    
    def get(self, request):
        """Get performance metrics"""
        try:
            # Get cached performance metrics
            cache_key = "performance_metrics"
            metrics = cache.get(cache_key)
            
            if not metrics:
                # Generate default metrics if cache is empty
                metrics = {
                    'total_requests': 0,
                    'avg_response_time': 0.0,
                    'error_rate': 0.0,
                    'active_connections': 0,
                    'cache_hit_rate': 0.0
                }
            
            return JsonResponse({
                'success': True,
                'metrics': metrics
            })
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# Real-Time API Endpoints for Phase 6
@method_decorator(login_required, name='dispatch')
class RealTimeConnectionView(View):
    """View for real-time connection management"""
    
    def post(self, request):
        """Establish real-time connection"""
        try:
            connection_type = request.POST.get('type', 'market_data')
            
            # Return connection details
            return JsonResponse({
                'success': True,
                'connection_type': connection_type,
                'websocket_url': f'/ws/{connection_type}/',
                'message': f'Real-time {connection_type} connection established'
            })
            
        except Exception as e:
            logger.error(f"Error establishing real-time connection: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class MarketDataStreamingView(View):
    """View for market data streaming control"""
    
    def post(self, request):
        """Start/stop market data streaming"""
        try:
            action = request.POST.get('action')  # 'start' or 'stop'
            symbol = request.POST.get('symbol')
            
            if not symbol:
                return JsonResponse({
                    'success': False,
                    'error': 'Symbol is required'
                }, status=400)
            
            if action == 'start':
                message = f'Started streaming market data for {symbol}'
            elif action == 'stop':
                message = f'Stopped streaming market data for {symbol}'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action. Use "start" or "stop"'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'action': action,
                'symbol': symbol,
                'message': message
            })
            
        except Exception as e:
            logger.error(f"Error controlling market data streaming: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class RealTimeNotificationsView(View):
    """View for real-time notification management"""
    
    def post(self, request):
        """Send real-time notification"""
        try:
            notification_type = request.POST.get('type')
            title = request.POST.get('title')
            message = request.POST.get('message')
            priority = request.POST.get('priority', 'medium')
            
            if not all([notification_type, title, message]):
                return JsonResponse({
                    'success': False,
                    'error': 'Type, title, and message are required'
                }, status=400)
            
            notification_broadcaster.broadcast_notification(
                user_id=request.user.id,
                notification_id=f"manual_{int(timezone.now().timestamp())}",
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Notification sent successfully'
            })
            
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(login_required, name='dispatch')
class WebSocketStatusView(View):
    """View for WebSocket connection status"""
    
    def get(self, request):
        """Get WebSocket connection status"""
        try:
            # Check if user has active WebSocket connections
            user_id = request.user.id
            
            # Get connection status from cache
            market_data_status = cache.get(f"ws_market_data_{user_id}", False)
            trading_signals_status = cache.get(f"ws_trading_signals_{user_id}", False)
            notifications_status = cache.get(f"ws_notifications_{user_id}", False)
            
            return JsonResponse({
                'success': True,
                'connections': {
                    'market_data': market_data_status,
                    'trading_signals': trading_signals_status,
                    'notifications': notifications_status
                },
                'websocket_urls': {
                    'market_data': '/ws/market-data/',
                    'trading_signals': '/ws/trading-signals/',
                    'notifications': '/ws/notifications/'
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting WebSocket status: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@login_required
def realtime_dashboard(request):
    """Real-time dashboard view for Phase 6"""
    return render(request, 'core/realtime_dashboard.html')


@login_required
def websocket_test(request):
    """WebSocket test page view for Phase 6"""
    return render(request, 'core/websocket_test.html')


@method_decorator(login_required, name='dispatch')
class WebSocketTestView(View):
    """View for running WebSocket tests"""
    
    def post(self, request):
        """Run WebSocket test"""
        try:
            import json
            data = json.loads(request.body)
            test_type = data.get('type', 'all')
            count = data.get('count', 5)
            delay = data.get('delay', 2.0)
            
            # Import the test command
            from django.core.management import call_command
            from io import StringIO
            
            # Capture command output
            out = StringIO()
            
            # Run the test command
            call_command(
                'test_websockets',
                type=test_type,
                count=count,
                delay=delay,
                stdout=out
            )
            
            output = out.getvalue()
            out.close()
            
            return JsonResponse({
                'success': True,
                'message': f'WebSocket test completed: {test_type}',
                'output': output
            })
            
        except Exception as e:
            logger.error(f"Error running WebSocket test: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


def run_websocket_test(request):
    """Function-based view for running WebSocket tests"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            test_type = data.get('type', 'all')
            count = data.get('count', 5)
            delay = data.get('delay', 2.0)
            
            # Import the test command
            from django.core.management import call_command
            from io import StringIO
            
            # Capture command output
            out = StringIO()
            
            # Run the test command
            call_command(
                'test_websockets',
                type=test_type,
                count=count,
                delay=delay,
                stdout=out
            )
            
            output = out.getvalue()
            out.close()
            
            return JsonResponse({
                'success': True,
                'message': f'WebSocket test completed: {test_type}',
                'output': output
            })
            
        except Exception as e:
            logger.error(f"Error running WebSocket test: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST method allowed'
    }, status=405)


def performance_metrics(request):
    """Get performance metrics"""
    try:
        # Get cached performance metrics
        cache_key = "performance_metrics"
        metrics = cache.get(cache_key)
        
        if not metrics:
            # Generate default metrics if cache is empty
            metrics = {
                'total_requests': 0,
                'avg_response_time': 0.0,
                'error_rate': 0.0,
                'active_connections': 0,
                'cache_hit_rate': 0.0
            }
        
        return JsonResponse({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
