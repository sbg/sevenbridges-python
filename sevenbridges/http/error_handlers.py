import logging
import time

import six
from requests.exceptions import HTTPError
from requests.packages.urllib3.exceptions import HTTPError as UrlLibHTTPError

from sevenbridges.compat import JSONDecodeError
from sevenbridges.decorators import retry_on_excs

logger = logging.getLogger(__name__)


@retry_on_excs(excs=(HTTPError, UrlLibHTTPError))
def rate_limit_sleeper(api, response):
    """
    Pauses the execution if rate limit is breached.
    :param api: Api instance.
    :param response: requests.Response object

    """
    while response.status_code == 429:
        headers = response.headers
        remaining_time = headers.get('X-RateLimit-Reset')
        sleep = int(remaining_time) - int(time.time())
        logger.warning('Rate limit reached! Waiting for [%s]s', sleep)
        time.sleep(sleep + 5)
        response = api.session.send(response.request)
    return response


@retry_on_excs(excs=(HTTPError, UrlLibHTTPError, JSONDecodeError))
def maintenance_sleeper(api, response, sleep=300):
    """
    Pauses the execution if sevenbridges api is under maintenance.
    :param api: Api instance.
    :param response: requests.Response object.
    :param sleep: Time to sleep in between the requests.
    """
    while response.status_code == 503:
        logger.info(
            'Service unavailable: Response=[%s]',
            six.text_type(response.__dict__)
        )
        response_body = response.json()
        if 'code' in response_body:
            if response_body['code'] == 0:
                logger.warning('API Maintenance in progress!'
                               ' Waiting for [%s]s', sleep)
                time.sleep(sleep)
                response = api.session.send(response.request)
            else:
                return response
        else:
            return response
    return response


@retry_on_excs(excs=(HTTPError, UrlLibHTTPError))
def general_error_sleeper(api, response, sleep=300):
    """
    Pauses the execution if response status code is > 500.
    :param api: Api instance.
    :param response: requests.Response object
    :param sleep: Time to sleep in between the requests.

    """
    while response.status_code >= 500:
        logger.warning(
            'Caught [%s] status code! Waiting for [%s]s',
            response.status_code,
            sleep
        )
        time.sleep(sleep)
        response = api.session.send(response.request)
    return response
