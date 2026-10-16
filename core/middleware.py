"""
Custom middleware for error handling and logging
"""
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django')


class UploadSizeLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in {'POST', 'PUT', 'PATCH'} and request.content_type == 'multipart/form-data':
            max_size = settings.MAX_UPLOAD_SIZE
            if any(
                uploaded_file.size > max_size
                for _, uploaded_files in request.FILES.lists()
                for uploaded_file in uploaded_files
            ):
                message = f'Each uploaded file must be {max_size // (1024 * 1024)} MB or smaller.'
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': message}, status=413)
                return HttpResponse(message, status=413)

        return self.get_response(request)


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


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""

    def process_response(self, request, response):
        """Add security headers"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
