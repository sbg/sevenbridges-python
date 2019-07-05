class PartSize:
    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB
    TB = 1024 * GB
    MAXIMUM_UPLOAD_SIZE = 5 * GB
    MAXIMUM_OBJECT_SIZE = 5 * TB
    MAXIMUM_TOTAL_PARTS = 10000

    DOWNLOAD_MINIMUM_PART_SIZE = 5 * MB
    UPLOAD_MINIMUM_PART_SIZE = 5 * MB


class TransferState:
    ABORTED = 'ABORTED'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    COMPLETED = 'COMPLETED'
    PREPARING = 'PREPARING'
    STOPPED = 'STOPPED'
    FAILED = 'FAILED'


class VolumeType:
    S3 = 'S3'
    GOOGLE = 'GCS'
    OSS = 'OSS'


class VolumeAccessMode:
    READ_ONLY = 'RO'
    READ_WRITE = 'RW'


class FileStorageType:
    VOLUME = 'VOLUME'
    PLATFORM = 'PLATFORM'


class FileApiFormats:
    FILE = 'File'
    FOLDER = 'Directory'


class ImportExportState:
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class TaskStatus:
    DRAFT = 'DRAFT'
    CREATING = 'CREATING'
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    ABORTED = 'ABORTED'
    ABORTING = 'ABORTING'
    FAILED = 'FAILED'


class FeedbackType:
    IDEA = 'IDEA'
    THOUGHT = 'THOUGHT'
    PROBLEM = 'PROBLEM'


class AppRawFormat:
    JSON = 'json'
    YAML = 'yaml'


class AppCopyStrategy:
    CLONE = 'clone'
    DIRECT = 'direct'
    TRANSIENT = 'transient'
    CLONE_DIRECT = 'clone_direct'


class AutomationRunActions:
    STOP = 'stop'


class AsyncJobStates:
    RUNNING = 'RUNNING'
    FINISHED = 'FINISHED'
    SUBMITTED = 'SUBMITTED'
    RESOLVING = 'RESOLVING'


class AsyncFileOperations:
    COPY = 'copy'
    DELETE = 'delete'
