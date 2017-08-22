import time

import faker
import requests

from sevenbridges.http.error_handlers import rate_limit_sleeper

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
