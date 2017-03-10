import faker
import pytest
import requests_mock

from sevenbridges import Api
from sevenbridges.tests.providers import (
    ProjectProvider, EndpointProvider, UserProvider, MemberProvider,
    FileProvider, AppProvider, TaskProvider,
    VolumeProvider)
from sevenbridges.tests.verifiers import (
    EndpointVerifier, ProjectVerifier, UserVerifier, MemberVerifier,
    FileVerifier, AppVerifier, TaskVerifier,
    VolumeVerifier)

generator = faker.Factory.create()

requests_mock.mock.case_sensitive = True


@pytest.fixture
def request_mocker(request):
    """
    :param request: pytest request object for cleaning up.
    :return: Returns instance of requests mocker used to mock HTTP calls.
    """
    m = requests_mock.Mocker()
    m.start()
    request.addfinalizer(m.stop)
    return m


class Precondition(object):
    """
    Aggregated data provided for all server side data mocking.
    """

    def __init__(self, request_mocker, base_url):
        self.user = UserProvider(request_mocker, base_url)
        self.endpoints = EndpointProvider(request_mocker, base_url)
        self.project = ProjectProvider(request_mocker, base_url)
        self.member = MemberProvider(request_mocker, base_url)
        self.file = FileProvider(request_mocker, base_url)
        self.app = AppProvider(request_mocker, base_url)
        self.task = TaskProvider(request_mocker, base_url)
        self.volume = VolumeProvider(request_mocker, base_url)


class Verifier(object):
    """
    Aggregated action verificator.
    """

    def __init__(self, request_mocker):
        self.user = UserVerifier(request_mocker)
        self.endpoints = EndpointVerifier(request_mocker)
        self.project = ProjectVerifier(request_mocker)
        self.member = MemberVerifier(request_mocker)
        self.file = FileVerifier(request_mocker)
        self.app = AppVerifier(request_mocker)
        self.task = TaskVerifier(request_mocker)
        self.volume = VolumeVerifier(request_mocker)


@pytest.fixture
def given(request_mocker, base_url):
    """
    Fixture returning Precondition.
    """
    return Precondition(request_mocker, base_url)


@pytest.fixture
def verifier(request_mocker):
    """
    Fixture returning Verificator.
    """
    return Verifier(request_mocker)


@pytest.fixture
def api(base_url):
    """
    Fixture returning instance of Api with randomly generated endpoint URL
    and authentication token.
    """
    return Api(base_url, token=generator.uuid4())


@pytest.fixture
def base_url():
    return generator.url()[:-1]


@pytest.fixture
def config_parser():
    class ConfigParser(object):
        def __init__(self, data):
            self.data = data

        def get(self, profile, item):
            return self.data[profile][item]

        def read(self, stream):
            pass

    class Mock(object):
        def __init__(self, data):
            self.data = data

        def __call__(self, *args, **kwargs):
            data = dict(kwargs)
            data.update(self.data)
            return ConfigParser(data)

    return Mock
