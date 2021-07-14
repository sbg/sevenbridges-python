import os
import time
import logging
import threading

from sevenbridges.errors import SbgError
from sevenbridges.http.client import generate_session
from sevenbridges.transfer.utils import Progress, total_parts
from sevenbridges.models.enums import (
    PartSize, TransferState, RequestParameters
)

logger = logging.getLogger(__name__)


def _get_part_url(api, url, upload, part):
    """
    Used by the worker to fetch url for the part that is to be uploaded.
    :param api: Api instance.
    :param url: Part url.
    :param upload: Upload identifier.
    :param part: Part number.
    :return: Storage generated URL for the part.
    """
    try:
        response = api.get(url.format(upload_id=upload, part_number=part))
        return response.json()['url']
    except Exception:
        raise SbgError(f'Unable to get upload url for part number {part}')


def _report_part(api, url, upload, part, e_tag):
    """
    Used by the worker to report the completion of the part upload.
    :param api: Api instance.
    :param url: Part url.
    :param upload: Upload identifier.
    :param part: Part number.
    :param e_tag: ETag
    """
    part_data = {
        'part_number': part,
        'response': {
            'headers': {
                'ETag': e_tag
            }
        }
    }
    try:
        api.post(url.format(upload_id=upload, part_number=''), data=part_data)
    except Exception as e:
        raise SbgError(f'Unable to report part number {part}. Reason: {e}')


def _submit_part(session, url, part, timeout):
    """
    Used by the worker to submit the part data to the storage service URL.
    :param session: Storage service session.
    :param url: Part url.
    :param part: Part data in bytes.
    :param timeout: Timeout for storage session.
    :return: ETag for the submitted part.
    """
    try:
        response = session.put(url, data=part, timeout=timeout)
        etag = response.headers.get('etag')
        return etag.strip('"') if etag else ""
    except Exception as e:
        raise SbgError(f'Failed to submit the part. Reason: {e}')


def _upload_part(api, session, url, upload, part_number, part, timeout):
    """
    Used by the worker to upload a part to the storage service.
    :param api: Api instance.
    :param session: Storage service session.
    :param url: Part url.
    :param upload: Upload identifier.
    :param part_number: Part number.
    :param part: Part data.
    :param timeout: Timeout for storage session.
    """
    part_url = _get_part_url(api, url, upload, part_number)
    e_tag = _submit_part(session, part_url, part, timeout)
    _report_part(api, url, upload, part_number, e_tag)


class UPartedFile:
    _URL = {
        'upload_part': '/upload/multipart/{upload_id}/part/{part_number}'
    }

    def __init__(
        self, fp, file_size, part_size, upload, timeout, storage_session, api
    ):

        """
        Emulates the partitioned file. Uses the upload pool attached to the
        api session to submit the file parts for uploading.

        :param fp: File descriptor.
        :param file_size: File size.
        :param part_size: Part size.
        :param upload: Upload identifier.
        :param timeout: Timeout for storage session service.
        :param storage_session: Storage session.
        :param api: Api instance.
        """
        self.fp = fp
        self.file_size = file_size
        self.part_size = part_size
        self.upload_id = upload
        self.timeout = timeout
        self.session = storage_session
        self.api = api
        self.pool = api.upload_pool
        self.submitted = 0
        self.total_submitted = 0
        self.total = total_parts(self.file_size, self.part_size) or 1
        self.parts = self.get_parts()

    def submit(self):

        """
        Partitions the file into chunks and submits them into group of 4
        for upload on the api upload pool.
        :return: Futures
        """
        futures = []
        while self.submitted < 4 and not self.done():
            part = self.parts.pop(0)
            part_number = part['part']
            part_read_offset = part['offset']
            part_read_limit = part['limit']

            self.fp.seek(part_read_offset)
            part_data = self.fp.read(part_read_limit - part_read_offset)

            futures.append(
                self.pool.submit(
                    _upload_part, self.api, self.session,
                    self._URL['upload_part'], self.upload_id,
                    part_number, part_data, self.timeout
                )
            )

            self.submitted += 1
            self.total_submitted += 1

        return futures

    def done(self):
        return self.total_submitted == self.total

    def __iter__(self):
        futures = self.submit()
        while futures:
            future = futures[0]
            self.submitted -= 1
            futures.remove(future)
            futures.extend(self.submit())
            yield future.result()

    def get_parts(self):
        """
        Partitions the file and saves the parts to be uploaded
        in memory.
        """
        parts = []
        start_byte = 0
        for i in range(1, self.total + 1):
            end_byte = start_byte + self.part_size
            if end_byte >= self.file_size - 1:
                end_byte = self.file_size
            parts.append({
                'part': i,
                'offset': start_byte,
                'limit': end_byte
            })
            start_byte = end_byte
        return parts


# noinspection PyCallingNonCallable,PyTypeChecker,PyProtectedMember
class Upload(threading.Thread):
    _URL = {
        'upload_init': '/upload/multipart',
        'upload_info': '/upload/multipart/{upload_id}',
        'upload_complete': '/upload/multipart/{upload_id}/complete'
    }

    def __init__(
        self, file_path, project=None, parent=None, file_name=None,
        overwrite=False, part_size=None, retry_count=None, timeout=None,
        api=None
    ):
        """
        Multipart File uploader.

        :param file_path: File path on the disc.
        :param project: Target project identifier.
        :param file_name: Optional file name.
        :param overwrite: If true will overwrite file on the server.
        :param part_size: Size of part in bytes.
        :param retry_count: Retry count.
        :param timeout: Timeout for s3/google session.
        :param api: Api instance.
        """
        threading.Thread.__init__(self)
        self.daemon = True

        self._validate_project_parent(parent, project)

        if not file_path:
            raise SbgError('File path is not valid.')

        if not os.path.isfile(file_path):
            raise SbgError(
                f'File path {file_path} is not a path to a valid file.'
            )
        if not api:
            raise SbgError('Api instance not provided!')

        if not file_name:
            self._file_name = os.path.basename(file_path)
        else:
            self._file_name = file_name

        self._part_size = part_size or PartSize.UPLOAD_RECOMMENDED_SIZE
        self._project = project
        self._parent = parent
        self._file_path = file_path
        self._file_size = os.path.getsize(self._file_path)

        self._verify_file_size()

        self._overwrite = overwrite
        self._retry = retry_count or RequestParameters.DEFAULT_RETRY_COUNT
        self._timeout = timeout or RequestParameters.DEFAULT_TIMEOUT
        self._api = api
        self._bytes_done = 0
        self._time_started = 0
        self._running = threading.Event()
        self._status = TransferState.PREPARING
        self._callback = None
        self._errorback = None
        self._progress_callback = None
        self._stop_signal = False
        self._result = None

        self.session = generate_session(
            pool_connections=self._api.pool_connections,
            pool_maxsize=self._api.pool_maxsize,
            pool_block=self._api.pool_block,
            proxies=self._api.session.proxies,
            retry_count=self._retry,
        )

    def __repr__(self):
        return f'<Upload: status={self.status}>'

    def result(self):
        return self._result

    def _validate_project_parent(self, parent, project):
        if not project and not parent:
            raise SbgError('Project or parent identifier is required.')
        if project and parent:
            raise SbgError(
                'Project and parent identifiers are mutually exclusive.'
            )

    def _verify_file_size(self):
        """
        Verifies that the file is smaller then 5TB which is the maximum
        that is allowed for upload.
        """
        if self._file_size > PartSize.MAXIMUM_OBJECT_SIZE:
            self._status = TransferState.FAILED
            raise SbgError(
                f'File size = {self._file_size}b. '
                f'Maximum file size is {PartSize.MAXIMUM_OBJECT_SIZE}b'
            )

    def _initialize_upload(self):
        """
        Initialized the upload on the API server by submitting the information
        about the project, the file name, file size and the part size that is
        going to be used during multipart upload.
        """
        init_data = self._create_init_data()

        init_params = {}
        if self._overwrite:
            init_params['overwrite'] = self._overwrite

        try:
            response = self._api.post(
                self._URL['upload_init'], data=init_data, params=init_params
            )
            data = response.json()
            self._upload_id = data['upload_id']
            part_size = data.get('part_size')
            if part_size and part_size != self._part_size:
                logger.debug('Part size optimized by server to %s', part_size)
                self._part_size = part_size
        except SbgError as e:
            self._status = TransferState.FAILED
            raise SbgError(
                'Unable to initialize upload! Failed to get upload id! '
                f'Reason: {e.message}'
            )

    def _create_init_data(self):
        init_data = {
            'name': self._file_name,
            'size': self._file_size,
        }
        if self._part_size:
            init_data['part_size'] = self._part_size
        if self._project:
            init_data['project'] = self._project
        elif self._parent:
            init_data['parent'] = self._parent
        return init_data

    def _finalize_upload(self):
        """
        Finalizes the upload on the API server.
        """
        from sevenbridges.models.file import File
        try:
            response = self._api.post(
                self._URL['upload_complete'].format(upload_id=self._upload_id)
            ).json()
            # noinspection PyArgumentList
            self._result = File(api=self._api, **response)
            self._status = TransferState.COMPLETED

        except SbgError as e:
            self._status = TransferState.FAILED
            raise SbgError(
                f'Failed to complete upload! Reason: {e.message}'
            )

    def _abort_upload(self):
        """
        Aborts the upload on the API server.
        """
        try:
            self._api.delete(
                self._URL['upload_info'].format(upload_id=self._upload_id)
            )
        except SbgError as e:
            self._status = TransferState.FAILED
            raise SbgError(
                f'Failed to abort upload! Reason: {e.message}'
            )

    @property
    def progress(self):
        return self._bytes_done / (float(self._file_size) * 100) or 1

    @property
    def status(self):
        return self._status

    @property
    def start_time(self):
        return self._time_started

    @property
    def duration(self):
        return (time.time() - self._time_started) * 1000

    @property
    def file_name(self):
        return self._file_name

    def add_callback(self, callback=None, errorback=None):
        """
        Adds a callback that will be called when the upload
        finishes successfully or when error is raised.
        """
        self._callback = callback
        self._errorback = errorback

    def add_progress_callback(self, callback=None):
        """
        Adds a progress callback that will be called each time
        a get_parts is successfully uploaded. The first argument of the
        progress callback will be a progress object described in
        sevenbridges.transfer.utils

        :param callback: Callback function
        """
        self._progress_callback = callback

    def pause(self):
        """
        Pauses the upload.
        :raises SbgError: If upload is not in RUNNING state.
        """
        if self._status == TransferState.RUNNING:
            self._running.clear()
            self._status = TransferState.PAUSED
        else:
            raise SbgError('Can not pause. Upload not in RUNNING state.')

    def stop(self):
        """
        Stops the upload.
        :raises SbgError: If upload is not in PAUSED or RUNNING state.
        """
        if self.status in (TransferState.PAUSED, TransferState.RUNNING):
            self._running.clear()
            self._stop_signal = True
            self.join()
            self._abort_upload()
            self._status = TransferState.STOPPED
            if self._callback:
                return self._callback(self._status)
        else:
            raise SbgError(
                'Can not stop. Upload not in PAUSED or RUNNING state.'
            )

    def resume(self):
        """
        Resumes the upload that was paused.
        :raises SbgError: If upload is not in PAUSED state.
        """
        if self.status == TransferState.PAUSED:
            self._running.set()
            self._status = TransferState.RUNNING
        else:
            raise SbgError('Can not resume. Upload not in PAUSED state.')

    def wait(self):
        """
        Blocks until upload is completed.
        """
        self.join()

    def start(self):
        """
        Starts the upload.
        :raises SbgError: If upload is not in PREPARING state.
        """
        if self._status == TransferState.PREPARING:
            super().start()
        else:
            raise SbgError(
                'Unable to start. Upload not in PREPARING state.'
            )

    def run(self):
        """
        Runs the thread! Should not be used use start() method instead.
        """
        self._running.set()
        self._status = TransferState.RUNNING
        self._time_started = time.time()

        # Initializes the upload
        self._initialize_upload()

        # Opens the file for reading in binary mode.
        try:
            with open(self._file_path, mode='rb') as fp:
                # Creates a partitioned file
                parted_file = self.partition_file(fp)

                # Iterates over parts and submits them for upload.
                for _ in parted_file:
                    if self._stop_signal:
                        return
                    self._running.wait()
                    self._bytes_done += self._part_size
                    # If the progress callback is set we need to provide a
                    # progress object for it.
                    if self._progress_callback:
                        progress = Progress(
                            parted_file.total, parted_file.total_submitted,
                            self._bytes_done, self._file_size, self.duration
                        )
                        self._progress_callback(progress)
        except IOError:
            raise SbgError(f'Unable to open file {self._file_path}')
        except Exception as e:
            # If the errorback callback is set call it with status
            self._status = TransferState.FAILED
            if self._errorback:
                self._errorback(self._status)
            else:
                raise SbgError(str(e))

        # Finalizes the upload.
        self._finalize_upload()
        self._status = TransferState.COMPLETED
        # If the callback is set call it.
        if self._callback:
            self._callback(self._status)

    def partition_file(self, fp):
        return UPartedFile(
            fp, self._file_size, self._part_size, self._upload_id,
            self._timeout, self.session, self._api
        )


class CodePackageUPartedFile(UPartedFile):

    _URL = {
        'upload_part': '/automation/upload/{upload_id}/part/{part_number}'
    }


class CodePackageUpload(Upload):
    _URL = {
        'upload_init': '/automation/upload',
        'upload_info': '/automation/upload/{upload_id}',
        'upload_complete': '/automation/upload/{upload_id}/complete'
    }

    def __init__(
        self, file_path, automation_id, file_name=None, part_size=None,
        retry_count=RequestParameters.DEFAULT_RETRY_COUNT,
        timeout=RequestParameters.DEFAULT_TIMEOUT, parent=None, api=None
    ):
        """
            Multipart File uploader for automation code packages.

            "overwrite" input is disabled as we don't allow overwriting
            code packages.

            :param file_path: File path on the disc.
            :param automation_id: ID of the automation to which
            the package is uploaded.
            :param file_name: Optional file name.
            :param part_size: Size of part in bytes.
            :param retry_count: Retry count.
            :param timeout: Timeout for s3/google session.
            :param api: Api instance.
        """
        super().__init__(
            file_path=file_path,
            project=None,
            parent=parent,
            file_name=file_name,
            overwrite=False,
            part_size=part_size,
            retry_count=retry_count,
            timeout=timeout,
            api=api
        )
        if self._file_size == 0:
            raise SbgError('File size must not be 0.')

        self._automation_id = automation_id

    def _validate_project_parent(self, parent, project):
        # Skip for code packages
        pass

    def partition_file(self, fp):
        return CodePackageUPartedFile(
            fp, self._file_size, self._part_size, self._upload_id,
            self._timeout, self.session, self._api
        )

    def _create_init_data(self):
        init_data = {
            'name': self._file_name,
            'size': self._file_size,
            'automation_id': self._automation_id
        }
        if self._part_size:
            init_data['part_size'] = self._part_size
        return init_data
