from rest_framework.response import Response
from rest_framework import status

from apps.common.constants import (
    STATUS,
    DATA,
    MESSAGE,
    SUCCESS,
    ERROR,
    ERRORS,
)


def create_error_response(message: str, errors: list, status_code: status):
    return Response(
        {
            STATUS: ERROR,
            MESSAGE: message,
            DATA: {},
            ERRORS: errors,
        },
        status=status_code,
    )


def create_success_response(message: str, data: list[dict], status_code: status):
    return Response(
        {
            STATUS: SUCCESS,
            MESSAGE: message,
            DATA: data,
            ERRORS: {},
        },
        status=status_code,
    )
