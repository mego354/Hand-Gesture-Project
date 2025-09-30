"""
Custom middleware for logging, security, and error handling
"""
import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings
import json

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """Middleware for security enhancements"""
    
    def process_request(self, request):
        # Add security headers
        request.META['HTTP_X_CONTENT_TYPE_OPTIONS'] = 'nosniff'
        request.META['HTTP_X_FRAME_OPTIONS'] = 'DENY'
        request.META['HTTP_X_XSS_PROTECTION'] = '1; mode=block'
        
        # Generate request ID for tracking
        request.request_id = str(uuid.uuid4())
        
        # Log suspicious activity
        if self.is_suspicious_request(request):
            logger.warning(f"Suspicious request detected: {request.request_id} - {request.META.get('REMOTE_ADDR')}")
    
    def is_suspicious_request(self, request):
        """Check for suspicious request patterns"""
        suspicious_patterns = [
            'script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            '../', '..\\', 'cmd.exe', 'powershell', 'eval('
        ]
        
        # Check URL
        url_lower = request.get_full_path().lower()
        if any(pattern in url_lower for pattern in suspicious_patterns):
            return True
        
        # Check POST data
        if request.method == 'POST':
            try:
                post_data = str(request.POST)
                if any(pattern in post_data.lower() for pattern in suspicious_patterns):
                    return True
            except:
                pass
        
        return False


class LoggingMiddleware(MiddlewareMixin):
    """Middleware for request/response logging"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request details
        logger.info(f"Request started: {request.request_id} - {request.method} {request.get_full_path()}")
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log response details
            logger.info(f"Request completed: {request.request_id} - {response.status_code} - {duration:.3f}s")
            
            # Add performance headers
            response['X-Request-ID'] = request.request_id
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def process_exception(self, request, exception):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        
        # Log exception details
        logger.error(f"Request failed: {request.request_id} - {type(exception).__name__}: {str(exception)} - {duration:.3f}s")
        
        # Return appropriate error response
        if isinstance(exception, PermissionDenied):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        if settings.DEBUG:
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(exception),
                'request_id': request.request_id
            }, status=500)
        else:
            return JsonResponse({
                'error': 'Internal server error',
                'request_id': request.request_id
            }, status=500)


class RateLimitMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.requests = {}
        self.max_requests = 100  # requests per minute
        self.window_size = 60  # seconds
    
    def process_request(self, request):
        client_ip = request.META.get('REMOTE_ADDR')
        current_time = time.time()
        
        # Clean old entries
        self.clean_old_entries(current_time)
        
        # Check rate limit
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            self.requests[client_ip].append(current_time)
        else:
            self.requests[client_ip] = [current_time]
    
    def clean_old_entries(self, current_time):
        """Remove entries older than window_size"""
        cutoff_time = current_time - self.window_size
        for ip in list(self.requests.keys()):
            self.requests[ip] = [t for t in self.requests[ip] if t > cutoff_time]
            if not self.requests[ip]:
                del self.requests[ip]
