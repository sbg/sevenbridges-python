import os

from sevenbridges.errors import SbgError
from six.moves import configparser as cp


# noinspection PyBroadException
class ConfigUtils(object):
    """
        Utility class for parsing configuration files.
    """

    def __init__(self, parser):

        self.parser = parser

    def get_key(self, profile, key):
        try:
            return self.parser.get(profile, key)
        except:
            return None

    def get_items(self, key):
        try:
            return self.parser.items(key)
        except:
            return None


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
            self.proxies = proxies

        elif oauth_token and url:
            self.oauth_token = oauth_token
            self.api_url = url
            self.auth_token = token
            self.proxies = proxies

        elif profile is None:
            # If there is no profile check environmental variables.
            self.auth_token = os.environ.get('AUTH_TOKEN')
            self.oauth_token = os.environ.get('OAUTH_TOKEN')
            self.api_url = os.environ.get('API_URL')
            if not self.auth_token and not self.oauth_token:
                raise SbgError(
                    'auth-token or oauth-token environment variable missing.'
                )
            if not self.api_url:
                raise SbgError('api-url variable environment missing.')

        else:
            config_parser = cp.ConfigParser()
            user_config_path = os.path.join(os.path.expanduser('~'), '.sbgrc')
            config_parser.read(user_config_path)

            utils = ConfigUtils(parser=config_parser)

            self.auth_token = utils.get_key(profile, 'auth-token')
            self.oauth_token = utils.get_key(profile, 'oauth-token')
            proxy_values = utils.get_items('proxies')
            if proxy_values:
                self.proxies = {}
                for protocol, uri in proxy_values:
                    self.proxies[protocol] = uri
            else:
                self.proxies = None

            if not self.auth_token and not self.oauth_token:
                raise SbgError(
                    'auth-token or oauth-token variable missing in the '
                    'configuration file.'
                )
            self.api_url = utils.get_key(profile, 'api-url')
            if not self.api_url:
                raise SbgError('api-url missing in the configuration file.')
