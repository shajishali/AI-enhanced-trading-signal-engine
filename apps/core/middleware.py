import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor API performance and response times"""
    
    def process_request(self, request):
        """Record request start time"""
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Calculate and log response time"""
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            
            # Log slow responses (>500ms)
            if response_time > 0.5:
                logger.warning(
                    f"Slow response: {request.path} took {response_time:.3f}s "
                    f"({response.status_code})"
                )
            
            # Add response time header
            response['X-Response-Time'] = f"{response_time:.3f}s"
            
            # Track performance metrics in cache
            self._track_performance_metrics(request.path, response_time, response.status_code)
        
        return response
    
    def _track_performance_metrics(self, path, response_time, status_code):
        """Track performance metrics for monitoring"""
        try:
            # Create cache key for this endpoint
            cache_key = f"perf_metrics_{path.replace('/', '_')}"
            
            # Get existing metrics or create new ones
            metrics = cache.get(cache_key, {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'error_count': 0,
                'last_updated': None
            })
            
            # Update metrics
            metrics['count'] += 1
            metrics['total_time'] += response_time
            metrics['avg_time'] = metrics['total_time'] / metrics['count']
            metrics['min_time'] = min(metrics['min_time'], response_time)
            metrics['max_time'] = max(metrics['max_time'], response_time)
            
            if status_code >= 400:
                metrics['error_count'] += 1
            
            metrics['last_updated'] = time.time()
            
            # Cache for 1 hour
            cache.set(cache_key, metrics, 3600)
            
        except Exception as e:
            logger.error(f"Error tracking performance metrics: {e}")


class APIRateLimitMiddleware(MiddlewareMixin):
    """Middleware to implement basic API rate limiting"""
    
    def process_request(self, request):
        """Check rate limits for API requests"""
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Create rate limit key
        rate_limit_key = f"rate_limit_{client_ip}_{request.path}"
        
        # Check current request count
        request_count = cache.get(rate_limit_key, 0)
        
        # Set rate limit (100 requests per minute for API endpoints)
        if request_count >= 100:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.path}")
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': 60
            }, status=429)
        
        # Increment request count
        cache.set(rate_limit_key, request_count + 1, 60)  # 1 minute expiry
        
        return None
    
    def _get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip










