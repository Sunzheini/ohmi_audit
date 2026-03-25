"""
Django error handling middleware for consistent error responses.
"""

import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger('ohmi_audit')


def error_handling_middleware(get_response):
    """
    Centralized error handling middleware.
    
    - Catches unhandled exceptions
    - Returns appropriate error responses (JSON for API, HTML for web)
    - Logs all errors with request context
    - Hides sensitive details in production
    """

    def middleware(request):
        try:
            response = get_response(request)
            return response

        except Exception as e:
            # Log the error with full details
            request_id = getattr(request, 'request_id', 'unknown')
            logger.error(
                f"[{request_id}] Unhandled exception: {type(e).__name__}: {str(e)} "
                f"at {request.method} {request.path}",
                exc_info=True,
                extra={
                    'request_id': request_id,
                    'path': request.path,
                    'method': request.method,
                    'user': str(request.user),
                    'ip': request.META.get('REMOTE_ADDR', 'unknown'),
                }
            )

            # Determine if request expects JSON (API endpoint)
            is_api_request = (
                request.path.startswith('/api') or
                request.content_type == 'application/json' or
                request.META.get('HTTP_ACCEPT', '').startswith('application/json')
            )

            # Production vs Development responses
            if settings.DEBUG:
                # In development, let Django's default error page show
                raise

            # Production error responses
            if is_api_request:
                # JSON response for API endpoints
                return JsonResponse(
                    {
                        'error': 'Internal server error',
                        'message': 'An unexpected error occurred. Please try again later.',
                        'request_id': request_id,
                    },
                    status=500
                )
            else:
                # HTML response for web pages
                return render(
                    request,
                    '500.html',
                    {
                        'error_message': 'An unexpected error occurred. Please try again later.',
                        'request_id': request_id,
                    },
                    status=500
                )

    return middleware
