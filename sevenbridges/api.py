from concurrent.futures import ThreadPoolExecutor

from requests.adapters import DEFAULT_POOLSIZE

from sevenbridges.errors import SbgError
from sevenbridges.http.client import HttpClient

from sevenbridges.models.app import App
from sevenbridges.models.file import File
from sevenbridges.models.task import Task
from sevenbridges.models.team import Team
from sevenbridges.models.user import User
from sevenbridges.models.marker import Marker
from sevenbridges.models.volume import Volume
from sevenbridges.models.actions import Actions
from sevenbridges.models.dataset import Dataset
from sevenbridges.models.invoice import Invoice
from sevenbridges.models.project import Project
from sevenbridges.models.division import Division
from sevenbridges.models.async_jobs import AsyncJob
from sevenbridges.models.endpoints import Endpoints
from sevenbridges.models.rate_limit import RateLimit
from sevenbridges.models.storage_export import Export
from sevenbridges.models.storage_import import Import
from sevenbridges.models.drs_import import DRSImportBulk
from sevenbridges.models.enums import RequestParameters
from sevenbridges.models.billing_group import BillingGroup
from sevenbridges.models.automation import (
    Automation, AutomationRun, AutomationPackage
)


class Api(HttpClient):
    """Api aggregates all resource classes into single place"""

    actions = Actions
    apps = App
    async_jobs = AsyncJob
    automations = Automation
    automation_runs = AutomationRun
    automation_packages = AutomationPackage
    billing_groups = BillingGroup
    datasets = Dataset
    divisions = Division
    drs_imports = DRSImportBulk
    endpoints = Endpoints
    exports = Export
    files = File
    imports = Import
    invoices = Invoice
    markers = Marker
    projects = Project
    rate_limit = RateLimit
    tasks = Task
    teams = Team
    users = User
    volumes = Volume

    def __init__(
            self, url=None, token=None, oauth_token=None, config=None,
            timeout=None, download_max_workers=16, upload_max_workers=16,
            proxies=None, error_handlers=None, advance_access=False,
            pool_connections=DEFAULT_POOLSIZE, pool_maxsize=100,
            pool_block=True, max_parallel_requests=100,
            retry_count=RequestParameters.DEFAULT_RETRY_COUNT,
            backoff_factor=RequestParameters.DEFAULT_BACKOFF_FACTOR,
            debug=False,
    ):
        """
        Initializes api object.

        :param url: Api url.
        :param token: Secure token.
        :param oauth_token: Oauth token.
        :param config: Configuration profile.
        :param timeout: Client timeout.
        :param download_max_workers: Max number of threads for download.
        :param upload_max_workers: Max number of threads for upload.
        :param proxies: Proxy settings if any.
        :param error_handlers: List of error handlers - callables.
        :param advance_access: If True advance access features will be enabled.
        :param pool_connections: The number of urllib3 connection pools to
            cache.
        :param pool_maxsize: The maximum number of connections to save in the
            pool.
        :param pool_block: Whether the connection pool should block for
            connections.
        :param max_parallel_requests: Number which indicates number of parallel
            requests, only useful for multi thread applications.
        :return: Api object instance.
        """
        if not debug and url and url.startswith('http:'):
            raise SbgError(
                'Seven Bridges api client requires https, '
                f'cannot initialize with url {url}'
            )

        super().__init__(
            url=url, token=token, oauth_token=oauth_token, config=config,
            timeout=timeout, proxies=proxies, error_handlers=error_handlers,
            advance_access=advance_access, pool_connections=pool_connections,
            pool_maxsize=pool_maxsize, pool_block=pool_block,
            max_parallel_requests=max_parallel_requests,
            retry_count=retry_count, backoff_factor=backoff_factor,
        )

        self.download_pool = ThreadPoolExecutor(
            max_workers=download_max_workers
        )
        self.upload_pool = ThreadPoolExecutor(max_workers=upload_max_workers)
