import os
import faker
import pytest

from sevenbridges import Config
from sevenbridges.errors import SbgError

generator = faker.Factory.create()


@pytest.mark.parametrize("token", [generator.uuid4(), None])
def test_url_token_implicit(base_url, token):
    if token:
        config = Config(url=base_url, token=token)
        assert config.api_url == base_url
        assert config.auth_token == token
    else:
        with pytest.raises(SbgError):
            _ = Config(url=base_url, token=token)


@pytest.mark.parametrize("token", [generator.uuid4(), None])
def test_url_oauth_token_implicit(base_url, token):
    if token:
        config = Config(url=base_url, oauth_token=token)
        assert config.api_url == base_url
        assert config.oauth_token == token
    else:
        with pytest.raises(SbgError):
            _ = Config(url=base_url, oauth_token=token)


def test_os_environ_config(base_url, monkeypatch):
    mock_env = {
        'AUTH_TOKEN': 'token',
        'API_URL': base_url
    }
    monkeypatch.setattr(os, 'environ', mock_env)
    config = Config()
    assert config.api_url == base_url
    assert config.auth_token == 'token'
