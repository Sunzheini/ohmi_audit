"""
Django logging middleware for request/response tracking.
"""

import time
import logging
import uuid

logger = logging.getLogger('ohmi_audit')


def logging_middleware(get_response):
    """Enhanced middleware for structured request/response logging."""

    def middleware(request):
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id

        start_time = time.time()

        # Get client IP
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')

        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.path} from {client_ip}"
        )

        try:
            # Process the request
            response = get_response(request)
            process_time = time.time() - start_time

            # Log response
            status_code = response.status_code
            log_level = logging.INFO if status_code < 400 else logging.WARNING

            logger.log(
                log_level,
                f"[{request_id}] {status_code} {request.method} {request.path} - {process_time:.3f}s"
            )

            # Add tracking headers
            response['X-Request-ID'] = request_id
            response['X-Process-Time'] = f"{process_time:.3f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] ERROR {request.method} {request.path} - "
                f"{type(e).__name__}: {str(e)} - {process_time:.3f}s",
                exc_info=True
            )
            raise

    return middleware
