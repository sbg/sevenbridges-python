"""
sevenbridges-python
~~~~~~~~~~~~~~~~~~~
:copyright: 2020 Seven Bridges Genomics Inc.
:license: Apache 2.0
"""
import ssl
import logging

# Read and set version globally
# needs to be imported before other modules
from sevenbridges.version import __version__

from sevenbridges.api import Api
from sevenbridges.config import Config

from sevenbridges.models.invoice import Invoice
from sevenbridges.models.billing_group import (
    BillingGroup, BillingGroupBreakdown
)
from sevenbridges.models.user import User
from sevenbridges.models.endpoints import Endpoints
from sevenbridges.models.project import Project
from sevenbridges.models.task import Task
from sevenbridges.models.app import App
from sevenbridges.models.dataset import Dataset
from sevenbridges.models.bulk import BulkRecord
from sevenbridges.models.team import Team, TeamMember
from sevenbridges.models.member import Member, Permissions
from sevenbridges.models.file import File
from sevenbridges.models.storage_export import Export
from sevenbridges.models.storage_import import Import
from sevenbridges.models.volume import Volume
from sevenbridges.models.marker import Marker
from sevenbridges.models.division import Division
from sevenbridges.models.automation import (
    Automation, AutomationRun, AutomationPackage, AutomationMember
)
from sevenbridges.models.async_jobs import AsyncJob
from sevenbridges.models.compound.volumes.volume_object import VolumeObject

from sevenbridges.models.enums import (
    AppCopyStrategy, AppRawFormat, AsyncFileOperations, AsyncJobStates,
    AutomationRunActions, DivisionRole, FileStorageType, ImportExportState,
    TaskStatus, TransferState, VolumeAccessMode, VolumeType, PartSize,
)
from sevenbridges.errors import (
    SbgError, ResourceNotModified, ReadOnlyPropertyError, ValidationError,
    TaskValidationError, PaginationError, BadRequest, Unauthorized, Forbidden,
    NotFound, Conflict, TooManyRequests, ServerError, ServiceUnavailable,
    MethodNotAllowed, RequestTimeout, LocalFileAlreadyExists,
    ExecutionDetailsInvalidTaskType
)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    # Models
    'Api', 'AsyncJob', 'Automation', 'AutomationRun', 'AutomationMember',
    'AutomationPackage',  'Config', 'Invoice', 'BillingGroup',
    'BillingGroupBreakdown', 'User', 'Endpoints', 'Project', 'Task', 'App',
    'Member', 'Permissions', 'File', 'Export', 'Import', 'Volume',
    'VolumeObject', 'Marker', 'Division', 'Team', 'TeamMember', 'Dataset',
    'BulkRecord',
    # Enums
    'AppCopyStrategy', 'AppRawFormat', 'AppCopyStrategy',
    'AsyncFileOperations', 'AsyncJobStates', 'AutomationRunActions',
    'DivisionRole', 'FileStorageType', 'ImportExportState', 'TaskStatus',
    'TransferState', 'VolumeAccessMode', 'VolumeType', 'PartSize',
    # Errors
    'SbgError', 'ResourceNotModified', 'ReadOnlyPropertyError',
    'ValidationError', 'TaskValidationError', 'PaginationError', 'BadRequest',
    'Unauthorized', 'Forbidden', 'NotFound', 'Conflict', 'TooManyRequests',
    'ServerError', 'ServiceUnavailable', 'MethodNotAllowed', 'RequestTimeout',
    'LocalFileAlreadyExists', 'ExecutionDetailsInvalidTaskType',
    # Version
    '__version__',
]

required_ssl_version = (1, 0, 1)
if ssl.OPENSSL_VERSION_INFO < required_ssl_version:
    raise SbgError(
        'OpenSSL version included in this python version must be '
        'at least 1.0.1 or greater. Please update your environment build.'
    )
