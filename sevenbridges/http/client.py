import copy
import json
import logging
import platform
from datetime import datetime as dt

import requests

import sevenbridges
from sevenbridges.decorators import check_for_error
from sevenbridges.errors import SbgError, URITooLong
from sevenbridges.config import Config, format_proxies
from sevenbridges.http.error_handlers import maintenance_sleeper

logger = logging.getLogger(__name__)

client_info = {
    'version': sevenbridges.__version__,
    'os': platform.system(),
    'python': platform.python_version(),
    'requests': requests.__version__,
}


class AAHeader:
    key = 'X-Sbg-Advance-Access'
    value = 'Advance'


class RequestSession(requests.Session):
    """Client session class"""

    MAX_URL_LENGTH = 6000

    def send(self, request, **kwargs):
        """Send prepared request
        :param request: Prepared request to be sent
        :param kwargs: request keyword arguments
        :return: Request response
        """
        if len(request.url) > self.MAX_URL_LENGTH:
            raise URITooLong(
                message=(
                    'Request url too large, '
                    'likely too many query parameters provided.'
                )
            )
        return super(RequestSession, self).send(request, **kwargs)


def generate_session(proxies=None):
    """
    Utility method to generate request sessions.
    :param proxies: Proxies dictionary.
    :return: requests.Session object.
    """
    session = RequestSession()
    session.proxies = proxies
    return session


# noinspection PyBroadException
def config_vars(profiles, advance_access):
    """
    Utility method to fetch config vars using ini section profile
    :param profiles: profile name.
    :param advance_access: advance_access flag.
    :return:
    """
    for profile in profiles:
        try:
            config = Config(profile, advance_access=advance_access)
            url = config.api_endpoint
            token = config.auth_token
            proxies = config.proxies
            aa = config.advance_access
            return url, token, proxies, aa
        except Exception:
            pass
    return None, None, None, None


def mask_secrets(request_data):
    masked = copy.deepcopy(request_data)
    masked['headers']['X-SBG-Auth-Token'] = '*****'
    return masked


# noinspection PyTypeChecker
class HttpClient(object):
    """
    Implementation of all low-level API stuff, creating and sending requests,
    returning raw responses, authorization, etc.
    """

    def __init__(self, url=None, token=None, oauth_token=None, config=None,
                 timeout=None, proxies=None, error_handlers=None,
                 advance_access=False):

        if (url, token, config) == (None, None, None):
            url, token, proxies, advance_access = config_vars(
                [None, 'default'], advance_access
            )

        elif config is not None:
            url = config.api_endpoint
            token = config.auth_token
            proxies = config.proxies
            advance_access = advance_access or config.advance_access

        else:
            url = url
            token = token
            oauth_token = oauth_token
            proxies = format_proxies(proxies)
            advance_access = advance_access

        if not url:
            raise SbgError(
                'URL is missing! Configuration may contain errors, '
                'or the url parameter is missing.'
            )

        self.url = url.rstrip('/')
        self._session = generate_session(proxies)
        self.timeout = timeout
        self._limit = None
        self._remaining = None
        self._reset = None
        self._request_id = None
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent':
                'sevenbridges-python/{version} ({os}, Python/{python}; '
                'requests/{requests})'.format(**client_info)
        }
        self.timeout = timeout
        self.token = token
        self.oauth_token = oauth_token
        if self.token:
            self.headers['X-SBG-Auth-Token'] = token
        elif self.oauth_token:
            self.headers['Authorization'] = 'Bearer {}'.format(oauth_token)
        else:
            raise SbgError(
                'Required authorization model not selected!. '
                'Please provide at least one token value.'
            )

        self.aa = advance_access
        if self.aa:
            logger.warning(
                'Advance access features enabled. '
                'AA API calls can be subject to changes.'
            )
        self.error_handlers = [maintenance_sleeper]
        if error_handlers and isinstance(error_handlers, list):
            for handler in error_handlers:
                if handler not in self.error_handlers:
                    self.error_handlers.append(handler)

    @property
    def session(self):
        return self._session

    @property
    def limit(self):
        self._rate_limit()
        return int(self._limit) if self._limit else self._limit

    @property
    def remaining(self):
        self._rate_limit()
        return int(self._remaining) if self._remaining else self._remaining

    @property
    def reset_time(self):
        self._rate_limit()
        return dt.fromtimestamp(
            float(self._reset)
        ) if self._reset else self._reset

    @property
    def request_id(self):
        return self._request_id

    def add_error_handler(self, handler):
        if callable(handler) and handler not in self.error_handlers:
            self.error_handlers.append(handler)

    def remove_error_handler(self, handler):
        if callable(handler) and handler in self.error_handlers:
            self.error_handlers.remove(handler)

    def _rate_limit(self):
        self._request('GET', url='/rate_limit', append_base=True)

    @check_for_error
    def _request(self, verb, url, headers=None, params=None, data=None,
                 append_base=False, stream=False):
        if append_base:
            url = self.url + url
        if not headers:
            headers = self.headers
        else:
            headers.update(self.headers)
        if not self.token or self.oauth_token:
            raise SbgError(message='Api instance must be authenticated.')

        if hasattr(self, '_session_id'):
            if 'X-SBG-Auth-Token' in self.headers:
                del self.headers['X-SBG-Auth-Token']
            elif 'Authorization' in self.headers:
                del self.headers['Authorization']
            self.headers['X-SBG-Session-Id'] = getattr(self, '_session_id')

        # If advance access is enabled
        if self.aa:
            self.headers[AAHeader.key] = AAHeader.value

        request_data = {
            'verb': verb,
            'url': url,
            'headers': headers,
            'params': params
        }
        masked_request_data = mask_secrets(request_data)
        if not stream:
            masked_request_data.update({'data': data})
            logger.debug(
                "Request %s", masked_request_data,
                extra=masked_request_data
            )
            response = self._session.request(
                verb, url, params=params, data=json.dumps(data),
                headers=headers, timeout=self.timeout, stream=stream
            )
        else:
            logger.debug(
                'Stream Request %s', masked_request_data,
                extra=masked_request_data
            )
            response = self._session.request(
                verb, url, params=params, stream=stream, allow_redirects=True,
            )
        if self.error_handlers:
            for error_handler in self.error_handlers:
                response = error_handler(self, response)
        headers = response.headers
        self._limit = headers.get('X-RateLimit-Limit', self._limit)
        self._remaining = headers.get('X-RateLimit-Remaining', self._remaining)
        self._reset = headers.get('X-RateLimit-Reset', self._reset)
        self._last_response_time = response.elapsed.total_seconds()

        self._request_id = headers.get('X-Request-Id', self._request_id)
        return response

    def get(self, url, headers=None, params=None, data=None, append_base=True,
            stream=False):

        return self._request(
            'GET', url=url, headers=headers, params=params, data=data,
            append_base=append_base, stream=stream
        )

    def post(self, url, headers=None, params=None, data=None,
             append_base=True):
        return self._request('POST', url=url, headers=headers, params=params,
                             data=data, append_base=append_base)

    def put(self, url, headers=None, params=None, data=None, append_base=True):
        return self._request('PUT', url=url, headers=headers, params=params,
                             data=data, append_base=append_base)

    def patch(self, url, headers=None, params=None, data=None,
              append_base=True):
        return self._request('PATCH', url=url, headers=headers, params=params,
                             data=data, append_base=append_base)

    def delete(self, url, headers=None, params=None, append_base=True):
        return self._request('DELETE', url=url, headers=headers, params=params,
                             data={}, append_base=append_base)

    def __repr__(self):
        return '<API(%s) - "%s">' % (self.url, self.token)

    __str__ = __repr__
