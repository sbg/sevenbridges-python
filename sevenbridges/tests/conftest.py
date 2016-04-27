import pytest
import faker
import requests_mock

from sevenbridges import Api
from sevenbridges.tests.providers import (
    ProjectProvider, EndpointProvider, UserProvider, MemberProvider,
    FileProvider, AppProvider, TaskProvider
)
from sevenbridges.tests.verifiers import (
    EndpointVerifier, ProjectVerifier, UserVerifier, MemberVerifier,
    FileVerifier, AppVerifier, TaskVerifier
)

generator = faker.Factory.create()


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
