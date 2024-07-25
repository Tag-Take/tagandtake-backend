from rest_framework.response import Response


def create_error_response(message, errors, status_code):
    return Response(
        {
            "status": "error",
            "message": message,
            "data": {},
            "errors": errors,
        },
        status=status_code,
    )


def create_success_response(message, data, status_code):
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
            "errors": {},
        },
        status=status_code,
    )
