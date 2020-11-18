import logging
import functools
from six import raise_from

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import six
import requests

from sevenbridges.errors import (
    BadRequest, Unauthorized, Forbidden, NotFound, MethodNotAllowed,
    RequestTimeout, Conflict, TooManyRequests, SbgError, ServerError,
    ServiceUnavailable
)

logger = logging.getLogger(__name__)


def inplace_reload(method):
    """
    Executes the wrapped function and reloads the object
    with data returned from the server.
    """

    # noinspection PyProtectedMember
    def wrapped(obj, *args, **kwargs):
        in_place = True if kwargs.get('inplace') in (True, None) else False
        api_object = method(obj, *args, **kwargs)
        if in_place and api_object:
            obj._data = api_object._data
            obj._dirty = api_object._dirty
            obj._data.fetched = False
            return obj
        elif api_object:
            return api_object
        else:
            return obj

    return wrapped


def throttle(func):
    """Throttles number of parallel requests made by threads from single
    HttpClient session."""

    # noinspection PyProtectedMember
    @functools.wraps(func)
    def wrapper(http_client, *args, **kwargs):
        if http_client._throttle_limit:
            with http_client._throttle_limit:
                return func(http_client, *args, **kwargs)
        else:
            return func(http_client, *args, **kwargs)
    return wrapper


def check_for_error(func):
    """
    Executes the wrapped function and inspects the response object
    for specific errors.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            status_code = response.status_code
            if status_code in range(200, 204):
                return response
            if status_code == 204:
                return
            data = response.json()
            e = {
                400: BadRequest,
                401: Unauthorized,
                403: Forbidden,
                404: NotFound,
                405: MethodNotAllowed,
                408: RequestTimeout,
                409: Conflict,
                429: TooManyRequests,
                500: ServerError,
                503: ServiceUnavailable,
            }.get(status_code, SbgError)()
            if 'message' in data:
                e.message = data['message']
            if 'code' in data:
                e.code = data['code']
            if 'status' in data:
                e.status = data['status']
            if 'more_info' in data:
                e.more_info = data['more_info']
            raise e
        except requests.RequestException as e:
            raise SbgError(message=six.text_type(e))
        except JSONDecodeError:
            raise_from(
                ServiceUnavailable(message=six.text_type(
                    'Server response format is not JSON, '
                    'service might be unavailable.'
                )), None
            )
        except ValueError as e:
            raise SbgError(message=six.text_type(e))

    return wrapper
