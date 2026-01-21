import logging
import uuid
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger("conversations")


def prepare_exception_handler(exc, context):
    
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            error_message = "Validation error"
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_message = "Authentication failed"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_message = "Permission denied"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_message = "Resource not found"
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            error_message = "Method not allowed"
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            error_message = "Internal server error"
        else:
            error_message = "An error occurred"
        
        logger.error(f"API exception: {error_message}", exc_info=True, extra={
            "status_code": response.status_code,
            "exception_type": type(exc).__name__
        })
        
        response.data = {
            "code": response.status_code,
            "data": None,
            "message": error_message,
            "errors": response.data
        }
    else:
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
        return Response({
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "data": None,
            "message": "Internal Server Error",
            "errors": {"detail": "An unexpected error occurred. Please try again later."}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def validate_uuid(uuid_string, param_name="id"):
    """Validate UUID format and raise ValidationError if invalid"""
    try:
        uuid.UUID(str(uuid_string))
        return str(uuid_string)
    except (ValueError, TypeError, AttributeError):
        from rest_framework.exceptions import ValidationError
        raise ValidationError({param_name: [f"Invalid UUID format: '{uuid_string}'"]})


def prepare_success_response(data=None, message="Success", status_code=200):
    response_data = {
        "data": data,
        "message": message,
        "code": status_code
    }
    return Response(data=response_data, status=status_code)


def prepare_paginated_response(queryset, request, serializer_class, page_size=10, message=None):
    paginator = PageNumberPagination()
    paginator.page_size = page_size

    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True)
    paginated_data = paginator.get_paginated_response(serializer.data).data

    return Response(data=paginated_data, status=status.HTTP_200_OK)