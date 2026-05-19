"""
Custom middleware for error handling and logging
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django')

class ErrorHandlingMiddleware(MiddlewareMixin):
    """Custom middleware for handling errors"""
    
    def process_exception(self, request, exception):
        """Handle exceptions and return appropriate response"""
        logger.error(f"Exception: {exception}", exc_info=True)
        
        # For API requests, return JSON
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'An error occurred',
                'message': str(exception) if not request.is_secure() else 'Internal error'
            }, status=500)
        
        # For other requests, use default error handling
        return None


class AuditLoggingMiddleware(MiddlewareMixin):
    """Log all requests for audit trail"""
    
    def process_request(self, request):
        """Log incoming requests"""
        if request.user.is_authenticated:
            logger.info(f"User {request.user.username} - {request.method} {request.path}")
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        """Add security headers"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
