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
    CREDENTIALS = os.path.join(
        os.path.expanduser('~'),
        '.sevenbridges',
        'credentials'
    )
    CONFIG = os.path.join(
        os.path.expanduser('~'),
        '.sevenbridges',
        'sevenbridges-python',
        'config'
    )

    def __init__(self, profile):
        if not os.path.isfile(self.CREDENTIALS):
            raise SbgError('Missing credentials file.')

        self.profile = profile

        self.credentials_parser = cp.ConfigParser({
            'auth_token': None,
            'api_endpoint': None,
        }, allow_no_value=True)
        self.config_parser = cp.ConfigParser({
            'http_proxy': None,
            'https_proxy': None,
            'advance_access': False,
        }, allow_no_value=True)
        self.credentials_parser.read(self.CREDENTIALS)

        if not os.path.isfile(self.CONFIG):
            self.config_parser = None
            logging.info('No custom configuration present. Skipping...')
        else:
            self.config_parser = cp.ConfigParser({
                'http_proxy': None,
                'https_proxy': None,
                'advance_access': False,
            }, allow_no_value=True)
            self.config_parser.read(self.CONFIG)

    @property
    def api_endpoint(self):
        return self.credentials_parser.get(self.profile, 'api_endpoint')

    @property
    def auth_token(self):
        return self.credentials_parser.get(self.profile, 'auth_token')

    @property
    def proxies(self):
        try:
            return {
                'http_proxy': self.config_parser.get(
                    'proxies', 'http_proxy'
                ) if self.config_parser else None,
                'https_proxy': self.config_parser.get(
                    'proxies', 'https_proxy'
                ) if self.config_parser else None
            }
        except KeyError:
            return format_proxies({})
        except cp.NoSectionError:
            return format_proxies({})

    @property
    def advance_access(self):
        try:
            return bool(
                self.config_parser.get('mode', 'advance_access')
            ) if self.config_parser else False
        except KeyError:
            return False
        except cp.NoSectionError:
            return False


class Config(object):
    """
    Utility configuration class.
    """

    def __init__(self, profile=None, proxies=None, advance_access=None):
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
            self.advance_access = advance_access if advance_access else False
        else:
            cfg_profile = Profile(profile)
            self.auth_token = cfg_profile.auth_token
            self.api_endpoint = cfg_profile.api_endpoint
            self.advance_access = cfg_profile.advance_access

        if proxies:
            self.proxies = format_proxies(proxies)
        elif cfg_profile:
            self.proxies = format_proxies(cfg_profile.proxies)

        if advance_access:
            self.advance_access = advance_access
        elif cfg_profile:
            self.advance_access = cfg_profile.advance_access

        logger.info(
            'Client settings: [url={}] [token={}] [proxy={}]'.format(
                self.api_endpoint,
                self.auth_token,
                self.proxies
            )
        )
