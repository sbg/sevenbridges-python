import time

import faker
import pytest
import requests
import six

from sevenbridges.compat import JSONDecodeError
from sevenbridges.http.error_handlers import (
    rate_limit_sleeper, maintenance_sleeper, general_error_sleeper)

generator = faker.Factory.create()


class MockSession(object):
    def __init__(self, mock):
        self.mock = mock

    def send(self, response):
        return self.mock.pop()


def test_rate_limit_sleeper(api):
    resp429 = requests.Response()
    resp429.headers = {
        'X-RateLimit-Reset': time.time() + 1
    }
    resp429.status_code = 429
    resp200 = requests.Response()
    resp200.status_code = 200

    api._session = MockSession([resp429, resp200])
    resp = rate_limit_sleeper(api, resp429)

    assert resp.status_code == resp200.status_code


def test_maintenance_sleeper_invalid_json(api):
    resp503 = requests.Response()
    resp503.status_code = 503

    api._session = MockSession([resp503])
    with pytest.raises(JSONDecodeError):
        maintenance_sleeper(api, resp503, 1)


def test_maintenance_sleeper(api):
    resp503 = requests.Response()
    resp503.status_code = 503
    resp503._content = six.b('{"code": 0}')
    resp200 = requests.Response()
    resp200.status_code = 200

    api._session = MockSession([resp503, resp200])
    resp = maintenance_sleeper(api, resp503, 1)

    assert resp.status_code == resp200.status_code


def test_general_error_sleeper(api):
    resp500 = requests.Response()
    resp500.status_code = 500
    resp200 = requests.Response()
    resp200.status_code = 200

    api._session = MockSession([resp500, resp200])
    resp = general_error_sleeper(api, resp500, 1)

    assert resp.status_code == resp200.status_code
