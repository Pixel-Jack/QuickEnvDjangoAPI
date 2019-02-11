from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, transaction
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.response import Response


def set_rollback():
    atomic_requests = connection.settings_dict.get('ATOMIC_REQUESTS', False)
    if atomic_requests and connection.in_atomic_block:
        transaction.set_rollback(True)


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.
    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.
    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    # Django ValidationError
    if isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(detail=exc.messages)

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}

        set_rollback()
        return Response(get_full_details(data), status=exc.status_code, headers=headers)

    return None


def get_full_details(detail):
    if isinstance(detail, list):
        return [get_full_details(item) for item in detail]
    elif isinstance(detail, dict):
        return [repr_key_value(key, value) for key, value in detail.items()]
    return six.text_type(detail)


def repr_key_value(key, value):
    val = get_full_details(value)
    if isinstance(val, list):
        val = ' / '.join(val)
    if val == _('This field is required.'):
        return '{0}: {1}'.format(key, val)
    else:
        return val
