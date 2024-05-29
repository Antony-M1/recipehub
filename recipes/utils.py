import copy
from rest_framework.views import exception_handler
from rest_framework.response import Response
from .constant import RESPONSE_FAILED, RESPONSE_SUCSSS


def success_response(data=None, status=None):
    response = copy.deepcopy(RESPONSE_SUCSSS)
    response['data'] = data if data is not None else {}   
    return Response(response, status=status)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        _response = copy.deepcopy(RESPONSE_FAILED)
        _response['data'] = response.data
        response.data = _response
    
    return response
