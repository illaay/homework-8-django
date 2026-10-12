import logging
import time


logger = logging.getLogger('django.request')

class HTTPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start

        logger.info(
            'HTTP %s %s -> %s (%.3fs)',
            request.method,
            request.path,
            response.status_code,
            duration
        )
        return response