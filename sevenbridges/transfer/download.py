import os
import time
import logging
import hashlib
import threading

import requests

from sevenbridges.errors import SbgError
from sevenbridges.http.client import generate_session
from sevenbridges.models.enums import (
    PartSize, TransferState, RequestParameters
)
from sevenbridges.transfer.utils import Part, Progress, total_parts


logger = logging.getLogger(__name__)


def _download_part(path, session, url, timeout, start_byte, end_byte):
    """
    Downloads a single part.
    :param path: File path.
    :param session: Requests session.
    :param url: Url of the resource.
    :param timeout: Session timeout.
    :param start_byte: Start byte of the part.
    :param end_byte: End byte of the part.
    :return:
    """
    try:
        fp = os.open(path, os.O_CREAT | os.O_WRONLY)
    except IOError:
        raise SbgError('Unable to open file %s' % path)

    # Prepare range headers.
    headers = {}
    if end_byte is not None:
        headers['Range'] = 'bytes=%d-%d' % (int(start_byte), int(end_byte))

    try:
        response = session.get(
            url=url, headers=headers, timeout=timeout, stream=True
        )
        response.raise_for_status()
        part_size = response.headers.get('Content-Length')
        os.lseek(fp, start_byte, os.SEEK_SET)
        for part in response.iter_content(32 * PartSize.KB):
            os.write(fp, part)
        os.close(fp)
        return Part(start=start_byte, size=float(part_size))
    except (requests.HTTPError, requests.RequestException) as e:
        raise SbgError(f'Failed to download file. Response: {e}')


def _get_content_length(session, url, timeout):
    try:
        response = session.get(url, timeout=timeout, stream=True)
    except requests.RequestException as e:
        raise SbgError(str(e))

    file_size = response.headers.get('Content-Length', None)
    if file_size is None:
        raise SbgError('Server did not provide Content-Length Headers!')

    return file_size


class DPartedFile:
    def __init__(
            self, file_path, session, url, file_size, part_size, timeout, pool
    ):
        """
        Emulates the partitioned file. Uses the download pool attached to the
        api session to download file parts.
        :param file_path: Full path to the new file.
        :param session: Requests session.
        :param url: Resource url.
        :param file_size: Resource file size.
        :param part_size: Part size.
        :param timeout: Session timeout.
        :param pool: Download pool.
        """
        self.url = url
        self.file_path = file_path
        self.session = session
        self.file_size = file_size
        self.part_size = part_size
        self.timeout = timeout
        self.submitted = 0
        self.total_submitted = 0
        self.total = total_parts(self.file_size, self.part_size)
        self.pool = pool
        self.parts = self.get_parts()

    def submit(self):
        """
        Partitions the file into chunks and submits them into group of 4
        for download on the api download pool.
        """
        futures = []
        while self.submitted < 4 and not self.done():
            part = self.parts.pop(0)
            futures.append(
                self.pool.submit(
                    _download_part, self.file_path, self.session, self.url,
                    self.timeout, *part
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
        Partitions the file and saves the part information in memory.
        """
        parts = []
        start_b = 0
        end_byte = start_b + self.part_size - 1
        for _ in range(self.total):
            parts.append([start_b, end_byte])
            start_b = end_byte + 1
            end_byte = start_b + self.part_size - 1
        return parts


# noinspection PyCallingNonCallable,PyTypeChecker,PyProtectedMember
class Download(threading.Thread):
    def __init__(
            self, url, file_path, part_size=None, retry_count=None,
            timeout=None, api=None
     ):
        """
        File multipart downloader.
        :param url: URL of the file.
        :param file_path: Local file path.
        :param retry_count: Number of times to retry on error.
        :param timeout: Connection timeout in seconds.
        :param part_size: Size of the parts in bytes.
        :param api: Api instance.
        """
        threading.Thread.__init__(self)
        self.daemon = True

        if api is None:
            raise SbgError('Api instance missing.')

        if part_size and part_size < PartSize.DOWNLOAD_MINIMUM_PART_SIZE:
            self._status = TransferState.FAILED
            raise SbgError(
                f'Part size is too small! Minimum get_parts size '
                f'is {PartSize.DOWNLOAD_MINIMUM_PART_SIZE}'
            )

        self.url = url
        self._file_path = file_path

        # append unique suffix to the file
        suffix = hashlib.sha1(self._file_path.encode('utf-8')).hexdigest()[:10]
        self._temp_file = f'{self._file_path}.{suffix}'
        self._retry_count = (
            retry_count or RequestParameters.DEFAULT_RETRY_COUNT
        )
        self._timeout = timeout or RequestParameters.DEFAULT_TIMEOUT
        self._part_size = part_size or PartSize.DOWNLOAD_MINIMUM_PART_SIZE
        self._api = api
        self._bytes_done = 0
        self._running = threading.Event()
        self._callback = None
        self._errorback = None
        self._progress_callback = None
        self._time_started = 0

        self._session = generate_session(
            pool_connections=self._api.pool_connections,
            pool_maxsize=self._api.pool_maxsize,
            pool_block=self._api.pool_block,
            proxies=self._api.session.proxies,
            retry_count=self._retry_count,
        )

        try:
            self._file_size = self._get_file_size()
        except SbgError as error:
            if self._errorback:
                self._errorback(error)
            else:
                raise error
        self._status = TransferState.PREPARING
        self._stop_signal = False

    def __repr__(self):
        return f'<Download: status={self.status}>'

    @property
    def progress(self):
        return (self._bytes_done / self._file_size) * 100

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
    def path(self):
        return self._file_path

    def add_callback(self, callback=None, errorback=None):
        """
        Adds a callback that will be called when the download
        finishes successfully or when error is raised.
        """
        self._callback = callback
        self._errorback = errorback

    def add_progress_callback(self, callback=None):
        """
        Adds a progress callback that will be called each time
        a get_parts is successfully downloaded. The first argument of the
        progress callback will be a progress object described in
        sevenbridges.transfer.utils

        :param callback: Callback function
        """
        self._progress_callback = callback

    def pause(self):
        """
        Pauses the download.
        :raises SbgError: If upload is not in RUNNING state.
        """
        if self._status == TransferState.RUNNING:
            self._running.clear()
            self._status = TransferState.PAUSED
        else:
            raise SbgError('Can not pause. Download not in RUNNING state.')

    def stop(self):
        """
        Stops the download.
        :raises SbgError: If download is not in PAUSED or RUNNING state.
        """
        if self.status in (TransferState.PAUSED, TransferState.RUNNING):
            self._stop_signal = True
            self.join()
            self._status = TransferState.STOPPED
            if self._callback:
                return self._callback(self._status)
        else:
            raise SbgError(
                'Can not stop. Download not in PAUSED or RUNNING state.'
            )

    def resume(self):
        """
        Resumes the download.
        :raises SbgError: If download is not in RUNNING state.
        """
        if self._status != TransferState.PAUSED:
            self._running.set()
            self._status = TransferState.RUNNING
        else:
            raise SbgError('Can not pause. Download not in PAUSED state.')

    def wait(self):
        """
        Blocks until download is completed.
        """
        self.join()

    def start(self):
        """
        Starts the download.
        :raises SbgError: If download is not in PREPARING state.
        """
        if self._status == TransferState.PREPARING:
            self._running.set()
            super().start()
            self._status = TransferState.RUNNING
            self._time_started = time.time()
        else:
            raise SbgError(
                'Unable to start. Download not in PREPARING state.'
            )

    def run(self):
        """
        Runs the thread! Should not be used use start() method instead.
        """
        self._running.set()
        self._status = TransferState.RUNNING
        self._time_started = time.time()

        parted_file = DPartedFile(
            file_path=self._temp_file,
            session=self._session,
            url=self.url,
            file_size=self._file_size,
            part_size=self._part_size,
            timeout=self._timeout,
            pool=self._api.download_pool,
        )

        try:
            for part in parted_file:
                if self._stop_signal:
                    return
                self._running.wait()
                self._bytes_done += part.size
                if self._progress_callback:
                    progress = Progress(
                        parted_file.total, parted_file.total_submitted,
                        self._bytes_done, self._file_size, self.duration
                    )
                    self._progress_callback(progress)

        except Exception as exc:
            if self._errorback:
                return self._errorback(exc)
            else:
                raise SbgError('Download failed! %s' % str(exc))

        self._status = TransferState.COMPLETED
        try:
            os.rename(self._temp_file, self._file_path)
        except Exception as e:
            raise SbgError(f'Unable to rename the file due to an error: {e}.')

        if self._callback:
            return self._callback(self._status)

    def _get_file_size(self):
        """
        Fetches file size by reading the Content-Length header
        for the resource.
        :return: File size.
        """
        file_size = int(
            _get_content_length(self._session, self.url, self._timeout)
        )
        if file_size == 0:
            with open(self._temp_file, 'a', encoding='utf-8'):
                # Create file if empty
                pass
        return file_size
