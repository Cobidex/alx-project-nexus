from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that ensures all errors return a consistent response format.
    """
    # Call the default DRF exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Modify the response for standard API errors (400, 401, 403, 404, etc.)
        return Response({
            "status": "error",
            "message": response.data.get("detail", "An error occurred"),
            "errors": response.data if "detail" not in response.data else None,
        }, status=response.status_code)

    # Handle 500 errors separately
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return Response({
        "status": "error",
        "message": "A server error occurred. Please try again later."
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
