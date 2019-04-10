import time
import logging
import functools
import threading
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


def retry_on_excs(excs, retry_count=3, delay=5):
    """Retry decorator used to retry callables on for specific exceptions.

    :param excs: Exceptions tuple.
    :param retry_count: Retry count.
    :param delay: Delay in seconds between retries.
    :return: Wrapped function object.
    """

    def wrapper(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            for i in range(0, retry_count):
                try:
                    return f(*args, **kwargs)
                except excs:
                    if logger:
                        logger.warning(
                            'HTTPError caught.Retrying ...'.format(f.__name__),
                            exc_info=True
                        )
                    time.sleep(delay)
            else:
                logger.error(
                    '{} failed after {} retries'.format(
                        f.__name__, retry_count)
                )
            return f(*args, **kwargs)

        return deco

    return wrapper


def retry(retry_count):
    """
    Retry decorator used during file upload and download.
    """

    def func(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for backoff in range(retry_count):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    time.sleep(2 ** backoff)
            else:
                raise SbgError('{}: failed to complete: {}'.format(
                    threading.current_thread().getName(), f.__name__)
                )

        return wrapper

    return func


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
            message = (
                'Service might be unavailable. Can also occur by providing '
                'too many query parameters.'
            )
            raise_from(
                ServiceUnavailable(message=six.text_type(message)), None
            )
        except ValueError as e:
            raise SbgError(message=six.text_type(e))

    return wrapper
