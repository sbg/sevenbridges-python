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


class VolumeAccessMode:
    READ_ONLY = 'RO'
    READ_WRITE = 'RW'


class FileStorageType:
    VOLUME = 'VOLUME'
    PLATFORM = 'PLATFORM'


class ImportExportState:
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class TaskStatus:
    CREATING = 'CREATING'
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    ABORTED = 'ABORTED'
    FAILED = 'FAILED'
