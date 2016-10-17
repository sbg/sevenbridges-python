import hashlib
import os
import threading
import time

import requests
import six

from sevenbridges.errors import SbgError
from sevenbridges.http.client import generate_session
from sevenbridges.transfer.utils import Part, Progress, total_parts
from sevenbridges.models.enums import PartSize, TransferState


def _download_part(path, session, url, retry, timeout, start_byte, end_byte):
    """
    Downloads a single part.
    :param path: File path.
    :param session: Requests session.
    :param url: Url of the resource.
    :param retry: Number of times to retry on error.
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

    # Retry
    for retry in range(retry):
        try:
            response = session.get(
                url, headers=headers, timeout=timeout, stream=True
            )
            part_size = response.headers.get('Content-Length')
            os.lseek(fp, start_byte, os.SEEK_SET)
            for part in response.iter_content(32 * PartSize.KB):
                os.write(fp, part)
            os.close(fp)
        except requests.RequestException:
            time.sleep(2 ** retry)
            continue
        else:
            return Part(start=start_byte, size=float(part_size))

    else:
        os.close(fp)
        error = SbgError('Failed to download file after %s attempts.' % retry)
        raise error


class DPartedFile(object):
    def __init__(self, file_path, session, url, file_size, part_size, retry,
                 timeout,
                 pool):
        """
        Emulates the partitioned file. Uses the download pool attached to the
        api session to download file parts.
        :param file_path: Full path to the new file.
        :param session: Requests session.
        :param url: Resource url.
        :param file_size: Resource file size.
        :param part_size: Part size.
        :param retry: Number of times to retry on error.
        :param timeout: Session timeout.
        :param pool: Download pool.
        """
        self.url = url
        self.file_path = file_path
        self.session = session
        self.file_size = file_size
        self.part_size = part_size
        self.retry = retry
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
                    self.retry, self.timeout, *part)
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
        end_byte = start_b + PartSize.DOWNLOAD_MINIMUM_PART_SIZE - 1
        for i in range(self.total):
            parts.append([start_b, end_byte])
            start_b = end_byte + 1
            end_byte = start_b + PartSize.DOWNLOAD_MINIMUM_PART_SIZE - 1
        return parts


# noinspection PyCallingNonCallable,PyTypeChecker,PyProtectedMember
class Download(threading.Thread):
    def __init__(self, url, file_path,
                 part_size=PartSize.DOWNLOAD_MINIMUM_PART_SIZE, retry_count=5,
                 timeout=60, api=None):
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
                'Part size is too small! Minimum get_parts size is {}'.format(
                    PartSize.DOWNLOAD_MINIMUM_PART_SIZE)
            )

        # initializes the session

        self.url = url
        self._file_path = file_path

        # append unique suffix to the file
        self._temp_file = self._file_path + '.' + hashlib.sha1(
            self._file_path.encode('utf-8')).hexdigest()[:10]
        self._retry = retry_count
        self._timeout = timeout
        if part_size:
            self._part_size = part_size
        else:
            self._part_size = PartSize.DOWNLOAD_MINIMUM_PART_SIZE
        self._api = api
        self._bytes_done = 0
        self._running = threading.Event()
        self._callback = None
        self._errorback = None
        self._progress_callback = None
        self._time_started = 0

        self._session = generate_session(self._api.session.proxies)

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
        return six.text_type(
            '<Download: status={status}>'.format(status=self.status)
        )

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
        return time.time() - self._time_started

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
            super(Download, self).start()
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

        parted_file = DPartedFile(self._temp_file,
                                  self._session,
                                  self.url,
                                  self._file_size,
                                  self._part_size,
                                  self._retry,
                                  self._timeout,
                                  self._api.download_pool)

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
        except Exception:
            raise SbgError("Unable to rename the file.")

        if self._callback:
            return self._callback(self._status)

    def _get_file_size(self):
        """
        Fetches file size by reading the Content-Length header
        for the resource.
        :return: File size.
        """
        try:
            response = self._session.get(
                self.url, timeout=self._timeout, stream=True
            )
        except requests.RequestException as e:
            raise SbgError(str(e))

        file_size = response.headers.get('Content-Length', None)
        if not file_size:
            raise SbgError('Server did not provide Content-Length Headers!')

        if int(file_size) == 0:
            raise SbgError('File size is 0. Refusing to download.')

        return int(file_size)
