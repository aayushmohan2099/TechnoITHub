from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def standard_error_handler(exc, context):
    # Pehle DRF ka default exception handler call karein
    response = exception_handler(exc, context)

    # PDF Standards ke hisaab se Error Messages map karna[cite: 2]
    error_mapping = {
        400: "Bad Request: invalid input or business rule violation",
        401: "Unauthorized: missing or invalid authentication",
        403: "Forbidden: authenticated user lacks permission",
        404: "Not Found: requested resource does not exist or is not available to the user",
        409: "Conflict: duplicate employee/email or conflicting state",
        429: "Too Many Requests: rate limit exceeded",
        500: "Internal Server Error: unexpected server failure"
    }

    if response is not None:
        # Agar error DRF ne catch kar li hai (jaise 400, 401, 403, 404)
        status_code = response.status_code
        default_message = error_mapping.get(status_code, "An error occurred")
        
        # Standard JSON format banayein
        custom_response_data = {
            "error": default_message,
            "status_code": status_code,
            "details": response.data  # DRF ke actual validation errors yahan aayenge
        }
        response.data = custom_response_data
    else:
        # Agar Python code ftt gaya (Unhandled Exception -> 500)
        # Rule: Do not expose stack traces in production[cite: 2]
        custom_response_data = {
            "error": error_mapping[500],
            "status_code": 500,
            "details": "An unexpected error occurred on the server."
        }
        return Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response