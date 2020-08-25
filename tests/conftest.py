import faker
import pytest
import requests_mock

from sevenbridges import Api
from tests import providers, verifiers

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
        self.user = providers.UserProvider(request_mocker, base_url)
        self.endpoints = providers.EndpointProvider(request_mocker, base_url)
        self.rate = providers.RateLimitProvider(request_mocker, base_url)
        self.project = providers.ProjectProvider(request_mocker, base_url)
        self.member = providers.MemberProvider(request_mocker, base_url)
        self.file = providers.FileProvider(request_mocker, base_url)
        self.app = providers.AppProvider(request_mocker, base_url)
        self.task = providers.TaskProvider(request_mocker, base_url)
        self.volume = providers.VolumeProvider(request_mocker, base_url)
        self.action = providers.ActionProvider(request_mocker, base_url)
        self.division = providers.DivisionProvider(request_mocker, base_url)
        self.team = providers.TeamProvider(request_mocker, base_url)
        self.marker = providers.MarkerProvider(request_mocker, base_url)
        self.imports = providers.ImportsProvider(request_mocker, base_url)
        self.exports = providers.ExportsProvider(request_mocker, base_url)
        self.team_member = providers.TeamMemberProvider(
            request_mocker, base_url)
        self.datasets = providers.DatasetProvider(request_mocker, base_url)
        self.automations = providers.AutomationProvider(
            request_mocker, base_url)
        self.automation_runs = providers.AutomationRunProvider(
            request_mocker, base_url)
        self.automation_members = providers.AutomationMemberProvider(
            request_mocker, base_url
        )
        self.automation_packages = providers.AutomationPackageProvider(
            request_mocker, base_url
        )
        self.async_jobs = providers.AsyncJobProvider(request_mocker, base_url)
        self.cp_uploads = providers.CodePackageUploadProvider(
            request_mocker, base_url
        )
        self.uploads = providers.FileUploadProvider(request_mocker, base_url)


class Verifier(object):
    """
    Aggregated action verificator.
    """

    def __init__(self, request_mocker):
        self.user = verifiers.UserVerifier(request_mocker)
        self.endpoints = verifiers.EndpointVerifier(request_mocker)
        self.project = verifiers.ProjectVerifier(request_mocker)
        self.member = verifiers.MemberVerifier(request_mocker)
        self.file = verifiers.FileVerifier(request_mocker)
        self.app = verifiers.AppVerifier(request_mocker)
        self.task = verifiers.TaskVerifier(request_mocker)
        self.volume = verifiers.VolumeVerifier(request_mocker)
        self.action = verifiers.ActionVerifier(request_mocker)
        self.division = verifiers.DivisionVerifier(request_mocker)
        self.team = verifiers.TeamVerifier(request_mocker)
        self.marker = verifiers.MarkerVerifier(request_mocker)
        self.imports = verifiers.ImportsVerifier(request_mocker)
        self.exports = verifiers.ExportsVerifier(request_mocker)
        self.datasets = verifiers.DatasetVerifier(request_mocker)
        self.automations = verifiers.AutomationVerifier(request_mocker)
        self.automation_runs = verifiers.AutomationRunVerifier(request_mocker)
        self.automation_members = verifiers.AutomationMemberVerifier(
            request_mocker
        )
        self.async_jobs = verifiers.AsyncJobVerifier(request_mocker)
        self.automation_packages = verifiers.AutomationPackageVerifier(
            request_mocker
        )


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
