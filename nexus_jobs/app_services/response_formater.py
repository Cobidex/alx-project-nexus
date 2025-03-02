from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class CustomResponseMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if isinstance(response, Response) and response.status_code == 200:
            response.data = {
                "status": "success",
                "data": response.data
            }
        return response
