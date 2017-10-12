import os

import faker
from six.moves import configparser

from sevenbridges import Config, Api
from sevenbridges.config import Profile

generator = faker.Factory.create()


def test_os_environ_config(base_url, monkeypatch):
    mock_env = {
        'SB_AUTH_TOKEN': 'token',
        'SB_API_ENDPOINT': base_url
    }
    monkeypatch.setattr(os, 'environ', mock_env)
    config = Config()
    assert config.api_endpoint == base_url
    assert config.auth_token == 'token'


def test_os_environ_config_with_api(base_url, monkeypatch):
    mock_env = {
        'SB_AUTH_TOKEN': 'token',
        'SB_API_ENDPOINT': base_url,
        'HTTP_PROXY': base_url,
        'HTTPS_PROXY': base_url,
    }
    monkeypatch.setattr(os, 'environ', mock_env)

    api = Api()
    assert api.url == base_url
    assert api.token == 'token'
    api.session.proxies['http'] = mock_env['HTTP_PROXY']
    api.session.proxies['https'] = mock_env['HTTPS_PROXY']


def test_default_config(base_url, monkeypatch, config_parser):
    data = {
        'default': {
            'auth_token': 'token',
            'api_endpoint': base_url
        },
        'proxies': {
            'http_proxy': 'http',
            'https_proxy': 'https'
        }
    }
    parser = config_parser(data)
    monkeypatch.setattr(configparser, 'ConfigParser', parser)
    monkeypatch.setattr(os.path, 'isfile', lambda x: True)

    api = Api()
    assert api.session.proxies.get('http') == data['proxies']['http_proxy']
    assert api.session.proxies.get('https') == data['proxies']['https_proxy']


def test_config_profile(base_url, monkeypatch, config_parser):
    data = {
        'profile': {
            'auth_token': 'token',
            'api_endpoint': base_url
        },
        'proxies': {
            'http_proxy': 'http',
            'https_proxy': 'https'
        }
    }
    parser = config_parser(data)
    monkeypatch.setattr(configparser, 'ConfigParser', parser)
    monkeypatch.setattr(os.path, 'isfile', lambda x: True)

    api = Api(config=Config('profile'))
    assert api.url == data['profile']['api_endpoint']
    assert api.token == data['profile']['auth_token']


def test_config_profile_no_proxy(base_url, monkeypatch, config_parser):
    def is_file(f):
        if f == Profile.CREDENTIALS:
            return True
        else:
            return False

    data = {
        'profile': {
            'auth_token': 'token',
            'api_endpoint': base_url
        }
    }
    parser = config_parser(data)
    monkeypatch.setattr(configparser, 'ConfigParser', parser)
    monkeypatch.setattr(os.path, 'isfile', is_file)

    api = Api(config=Config('profile'))
    assert api.url == data['profile']['api_endpoint']
    assert api.token == data['profile']['auth_token']


def test_config_profile_explicit_proxy(base_url, monkeypatch, config_parser):
    def is_file(f):
        if f == Profile.CREDENTIALS:
            return True
        else:
            return False

    data = {
        'profile': {
            'auth_token': 'token',
            'api_endpoint': base_url
        }
    }

    proxies = {
        'http_proxy': 'http',
        'https_proxy': 'https'
    }
    parser = config_parser(data)
    monkeypatch.setattr(configparser, 'ConfigParser', parser)
    monkeypatch.setattr(os.path, 'isfile', is_file)

    api = Api(config=Config('profile', proxies=proxies))
    assert api.url == data['profile']['api_endpoint']
    assert api.token == data['profile']['auth_token']
    assert api.session.proxies.get('http') == proxies['http_proxy']
    assert api.session.proxies.get('https') == proxies['https_proxy']


def test_config_advance_access(base_url, monkeypatch, config_parser):
    def is_file(f):
        if f == Profile.CREDENTIALS or f == Profile.CONFIG:
            return True
        else:
            return False

    data = {
        'profile': {
            'auth_token': 'token',
            'api_endpoint': base_url
        },
        'mode': {
            'advance_access': True
        }
    }
    parser = config_parser(data)
    monkeypatch.setattr(configparser, 'ConfigParser', parser)
    monkeypatch.setattr(os.path, 'isfile', is_file)

    api = Api(config=Config('profile'))
    assert api.aa is True


def test_config_explicit_advance_access(base_url, monkeypatch, config_parser):
    def is_file(f):
        if f == Profile.CREDENTIALS or f == Profile.CONFIG:
            return True
        else:
            return False

    data = {
        'profile': {
            'auth_token': 'token',
            'api_endpoint': base_url
        }
    }
    parser = config_parser(data)
    monkeypatch.setattr(configparser, 'ConfigParser', parser)
    monkeypatch.setattr(os.path, 'isfile', is_file)

    api = Api(config=Config('profile'), advance_access=True)
    assert api.aa is True
