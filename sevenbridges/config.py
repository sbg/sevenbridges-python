import os

from sevenbridges.errors import SbgError
from six.moves import configparser as cp
from sevenbridges.http.client import format_proxies


class Config(object):
    """
    Utility configuration class.
    """

    def __init__(self, profile=None, url=None, token=None, oauth_token=None,
                 proxies=None):
        """
        Configures the bindings to use api url and token specified
        in the .ini like configuration file.
        :param profile: .ini section, if not supplied os.environ will be used.
        :param url: Api url.
        :param token: Authentication token.
        :param oauth_token: Oauth token.
        :param proxies: Proxy settings if any.

        """
        if token and url:
            self.auth_token = token
            self.api_url = url
            self.oauth_token = oauth_token
            self.proxies = format_proxies(proxies)

        elif oauth_token and url:
            self.oauth_token = oauth_token
            self.api_url = url
            self.auth_token = token
            self.proxies = format_proxies(proxies)

        elif profile is None:
            # If there is no profile check environmental variables.
            self.auth_token = os.environ.get('AUTH_TOKEN')
            self.oauth_token = os.environ.get('OAUTH_TOKEN')
            self.api_url = os.environ.get('API_URL')
            self.proxies = {
                'http-proxy': os.environ.get('HTTP_PROXY'),
                'https-proxy': os.environ.get('HTTPS_PROXY')
            }
            if not self.auth_token and not self.oauth_token:
                raise SbgError(
                    'auth-token or oauth-token environment variable missing.'
                )
            if not self.api_url:
                raise SbgError('api-url variable environment missing.')

        else:
            parser = cp.ConfigParser({
                'oauth-token': None,
                'auth-token': None,
                'api-url': None,
                'http-proxy': None,
                'https-proxy': None,
            })
            user_config_path = os.path.join(os.path.expanduser('~'), '.sbgrc')
            parser.read(user_config_path)

            parser.read(user_config_path)
            self.auth_token = parser.get(profile, 'auth-token')
            self.oauth_token = parser.get(profile, 'oauth-token')
            self.proxies = {
                'http-proxy': parser.get(profile, 'http-proxy'),
                'https-proxy': parser.get(profile, 'https-proxy')
            }
            if not self.auth_token and not self.oauth_token:
                raise SbgError(
                    'auth-token or oauth-token variable missing in the '
                    'configuration file.'
                )
            self.api_url = parser.get(profile, 'api-url')
            if not self.api_url:
                raise SbgError('api-url missing in the configuration file.')
