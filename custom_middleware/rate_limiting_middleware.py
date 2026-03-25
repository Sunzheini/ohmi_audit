"""
Django rate limiting middleware to prevent abuse and DDoS attacks.
"""

import time
from django.http import JsonResponse
from django.core.cache import cache


def rate_limiting_middleware(get_response):
    """
    Simple rate limiting middleware using Django cache.
    
    Limits:
    - 100 requests per minute per IP
    - 1000 requests per hour per IP
    
    Returns 429 (Too Many Requests) when limit is exceeded.
    """

    def middleware(request):
        # Skip rate limiting for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return get_response(request)

        # Get client IP
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Skip rate limiting for localhost in development
        if client_ip in ['127.0.0.1', 'localhost', '::1']:
            return get_response(request)

        # Rate limiting keys
        minute_key = f"rate_limit_minute:{client_ip}"
        hour_key = f"rate_limit_hour:{client_ip}"

        # Get current counts
        minute_count = cache.get(minute_key, 0)
        hour_count = cache.get(hour_key, 0)

        # Check limits
        if minute_count >= 100:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'limit': '100 requests per minute',
                },
                status=429
            )

        if hour_count >= 1000:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'limit': '1000 requests per hour',
                },
                status=429
            )

        # Increment counters
        if minute_count == 0:
            cache.set(minute_key, 1, 60)  # Expire in 60 seconds
        else:
            cache.incr(minute_key)

        if hour_count == 0:
            cache.set(hour_key, 1, 3600)  # Expire in 1 hour
        else:
            cache.incr(hour_key)

        # Add rate limit headers to response
        response = get_response(request)
        response['X-RateLimit-Limit-Minute'] = '100'
        response['X-RateLimit-Remaining-Minute'] = str(100 - minute_count - 1)
        response['X-RateLimit-Limit-Hour'] = '1000'
        response['X-RateLimit-Remaining-Hour'] = str(1000 - hour_count - 1)

        return response

    return middleware
