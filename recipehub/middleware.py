import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        logger.info(f"Request: {request.method} {request.get_full_path()}")
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        
        # Log the response status code
        logger.info(f"Response: {response.status_code}")


        return response

    def process_exception(self, request, exception):
        logger.critical(f"An error occurred: {exception}", exc_info=True)
        
        return JsonResponse({'status': 'Something went wrong', 'error':str(exception)}, status=500)