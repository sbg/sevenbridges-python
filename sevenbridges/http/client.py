import json
import logging
import platform
from datetime import datetime as dt

import requests

import sevenbridges
from sevenbridges.config import Config, format_proxies
from sevenbridges.decorators import check_for_error
from sevenbridges.errors import SbgError
from sevenbridges.http.error_handlers import maintenance_sleeper

log = logging.getLogger(__name__)

client_info = {
    'version': sevenbridges.__version__,
    'os': platform.system(),
    'python': platform.python_version(),
    'requests': requests.__version__,

}


def generate_session(proxies=None):
    """
    Utility method to generate request sessions.
    :param proxies: Proxies dictionary.
    :return: requests.Session object.
    """
    session = requests.Session()
    session.proxies = proxies
    return session


# noinspection PyBroadException
def config_vars(profiles):
    """
    Utility method to fetch config vars using ini section profile
    :param profiles: profile name.
    :return:
    """
    for profile in profiles:
        try:
            config = Config(profile)
            url = config.api_endpoint
            token = config.auth_token
            proxies = config.proxies
            return url, token, proxies
        except Exception as e:
            pass
    return None, None, None


# noinspection PyTypeChecker
class HttpClient(object):
    """
    Implementation of all low-level API stuff, creating and sending requests,
    returning raw responses, authorization, etc.
    """

    def __init__(self, url=None, token=None, oauth_token=None, config=None,
                 timeout=None, proxies=None, error_handlers=None):

        if (url, token, config) == (None, None, None):
            url, token, proxies = config_vars([None, 'default'])

        elif config is not None:
            url = config.api_endpoint
            token = config.auth_token
            proxies = config.proxies

        else:
            url = url
            token = token
            oauth_token = oauth_token
            proxies = format_proxies(proxies)

        if not url:
            raise SbgError('URL is missing!'
                           ' Configuration may contain errors, '
                           'or you forgot to pass the url param.')

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
            raise SbgError('Required authorization model not selected!. '
                           'Please provide at least one token value.'
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
            headers = headers.update(self.headers)
        if not self.token or self.oauth_token:
            raise SbgError(message='Api instance must be authenticated.')

        if hasattr(self, '_session_id'):
            if 'X-SBG-Auth-Token' in self.headers:
                del self.headers['X-SBG-Auth-Token']
            elif 'Authorization' in self.headers:
                del self.headers['Authorization']
            self.headers['X-SBG-Session-Id'] = getattr(self, '_session_id')

        d = {'verb': verb, 'url': url, 'headers': headers, 'params': params}
        if not stream:
            d.update({'data': data})
            log.debug("Request", extra=d)
            response = self._session.request(
                verb, url, params=params, data=json.dumps(data),
                headers=headers, timeout=self.timeout, stream=stream
            )
        else:
            log.debug('Stream Request', extra=d)
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
