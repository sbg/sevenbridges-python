import logging
import os

from six.moves import configparser as cp

from sevenbridges.errors import SbgError

logger = logging.getLogger(__name__)


def format_proxies(proxies):
    """
    Helper method for request proxy key compatibility.
    :param proxies: Proxies dictionary
    :return: Dict compatible with request proxy format.
    """
    if proxies:
        return {
            'http': proxies.get('http_proxy', None),
            'https': proxies.get('https_proxy', None)
        }
    return {}


class Profile(object):
    CREDENTIALS = os.path.join(os.path.expanduser('~'), '.sevenbridges',
                               'credentials')
    PROXIES = os.path.join(os.path.expanduser('~'), '.sevenbridges',
                           'sevenbridges-python', 'config')

    def __init__(self, profile):
        if not os.path.isfile(self.CREDENTIALS):
            raise SbgError('Missing credentials file.')

        self.profile = profile

        self.credentials_parser = cp.ConfigParser({
            'auth_token': None,
            'api_endpoint': None,
        })
        self.proxies_parser = cp.ConfigParser({
            'http_proxy': None,
            'api_endpoint': None
        })
        self.credentials_parser.read(self.CREDENTIALS)

        if not os.path.isfile(self.PROXIES):
            self.proxies_parser = None
            logging.info('No proxy configuration present. Skipping...')
        else:
            self.proxies_parser = cp.ConfigParser({
                'http_proxy': None,
                'https_proxy': None
            })
            self.proxies_parser.read(self.PROXIES)

    @property
    def api_endpoint(self):
        return self.credentials_parser.get(self.profile, 'api_endpoint')

    @property
    def auth_token(self):
        return self.credentials_parser.get(self.profile, 'auth_token')

    @property
    def proxies(self):
        return {
            'http_proxy': self.proxies_parser.get(
                'proxies', 'http_proxy') if self.proxies_parser else None,
            'https_proxy': self.proxies_parser.get(
                'proxies', 'https_proxy') if self.proxies_parser else None
        }


class Config(object):
    """
    Utility configuration class.
    """

    def __init__(self, profile=None, proxies=None):
        """
        Configures the bindings to use api url and token specified
        in the .ini like configuration file.
        :param profile: ini section, if not supplied [default] profile is used.
        """

        self.profile = profile

        cfg_profile = None

        if not self.profile:
            # Try os.environ
            self.auth_token = os.environ.get('SB_AUTH_TOKEN')
            self.api_endpoint = os.environ.get('SB_API_ENDPOINT')
            self.proxies = {
                'http': os.environ.get('HTTP_PROXY'),
                'https': os.environ.get('HTTPS_PROXY')
            }
            if not self.auth_token:
                logger.warning('Missing SB_AUTH_TOKEN os variable.')
                raise SbgError('Missing SB_AUTH_TOKEN')
            if not self.api_endpoint:
                logger.warning('Missing SB_API_ENDPOINT os variable.')
                raise SbgError('Missing SB_API_ENDPOINT')

        elif self.profile is 'default':
            cfg_profile = Profile('default')
            self.auth_token = cfg_profile.auth_token
            self.api_endpoint = cfg_profile.api_endpoint
        else:
            cfg_profile = Profile(profile)
            self.auth_token = cfg_profile.auth_token
            self.api_endpoint = cfg_profile.api_endpoint

        if proxies:
            self.proxies = format_proxies(proxies)
        elif cfg_profile:
            self.proxies = format_proxies(cfg_profile.proxies)

        logging.info(
            'Client settings: [url={}] [token={}] [proxy={}]'.format(
                self.auth_token,
                self.api_endpoint, self.proxies)

        )
