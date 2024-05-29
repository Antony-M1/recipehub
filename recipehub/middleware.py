import logging
import copy
from django.http import JsonResponse
from recipes.constant import RESPONSE_FAILED
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)

class CustomMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # self.is_authenticated(request)
        
        # if request.META.get("HTTP_AUTHORIZATION"):
        #     jwt_authenticator = JWTAuthentication()
        #     header = jwt_authenticator.get_header(request)
        #     raw_token = jwt_authenticator.get_raw_token(header)
        #     validated_token = jwt_authenticator.get_validated_token(raw_token)
        #     request.user = jwt_authenticator.get_user(validated_token)
        
        
        logger.info(f"Request: {request.method} {request.get_full_path()}")
        
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        
        # Log the response status code
        logger.info(f"Response: {response.status_code}")


        return response

    def process_exception(self, request, exception):
        logger.critical(f"An error occurred: {exception}", exc_info=True)
        
        response = copy.deepcopy(RESPONSE_FAILED)
        response['message'] = str(exception)
        
        return JsonResponse(response, status=500)
    
    
    def is_authenticated(self, request):
        
        if request.META.get("HTTP_AUTHORIZATION"):
            jwt_authenticator = JWTAuthentication()
            header = jwt_authenticator.get_header(request)
            if header is not None:
                raw_token = jwt_authenticator.get_raw_token(header)
                if raw_token is not None:
                    validated_token = None
                    try:
                        validated_token = jwt_authenticator.get_validated_token(raw_token)
                        request.user = jwt_authenticator.get_user(validated_token)
                    except InvalidToken:
                        request.user = AnonymousUser()
                    request.token = validated_token
                else:
                    request.user = AnonymousUser()
            else:
                request.user = AnonymousUser()