import os
import threading
import requests
import math
import time
import hashlib
from sevenbridges.errors import SbgError
from sevenbridges.transfer.utils import Chunk, PartSize, Progress, \
    TransferState


def _download_chunk(file_path, session, url, retry, timeout, start_byte,
                    end_byte):
    try:
        fp = os.open(file_path, os.O_CREAT | os.O_WRONLY)
    except IOError:
        raise SbgError('Unable to open file %s' % file_path)

    headers = {}
    if end_byte is not None:
        headers['Range'] = 'bytes=%d-%d' % (int(start_byte), int(end_byte))

    for retry in range(retry):
        try:
            response = session.get(
                url, headers=headers, timeout=timeout, stream=True
            )
            chunk_size = response.headers.get('Content-Length')
            os.lseek(fp, start_byte, os.SEEK_SET)
            for chunk in response.iter_content(32 * PartSize.KB):
                os.write(fp, chunk)
            os.close(fp)
        except requests.RequestException:
            time.sleep(2 ** retry)
            continue
        else:
            return Chunk(start=start_byte, size=float(chunk_size))

    else:
        os.close(fp)
        error = SbgError('Failed to download file after %s attempts.' % retry)
        raise error


class ChunkedFile(object):
    def __init__(self, file_path, session, url, file_size, chunk_size, retry,
                 timeout,
                 pool):
        self.url = url
        self.file_path = file_path
        self.session = session
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.retry = retry
        self.timeout = timeout
        self.submitted = 0
        self.total_submitted = 0
        self.total = self.total_chunks()
        self.pool = pool
        self.chunks = self.chunk()

    def submit(self):
        futures = []
        while self.submitted < 4 and not self.done():
            chunk = self.chunks.pop(0)
            futures.append(
                self.pool.submit(
                    _download_chunk, self.file_path, self.session, self.url,
                    self.retry, self.timeout, *chunk)
            )
            self.submitted += 1
            self.total_submitted += 1

        return futures

    def total_chunks(self):
        if self.file_size < self.chunk_size:
            return 1
        return int(math.ceil(self.file_size / self.chunk_size))

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

    def chunk(self):
        chunks = []
        start_b = 0
        end_byte = start_b + PartSize.DOWNLOAD_MINIMUM_PART_SIZE - 1
        for i in range(self.total):
            chunks.append([start_b, end_byte])
            start_b = end_byte + 1
            end_byte = start_b + PartSize.DOWNLOAD_MINIMUM_PART_SIZE - 1
        return chunks


# noinspection PyCallingNonCallable
class Download(threading.Thread):
    def __init__(self, url=None, file_path=None, retry=5, timeout=10,
                 chunk_size=None, api=None):
        """
        File downloader.
        :param url: URL of the file.
        :param file_path: Local file path.
        :param retry: Retry count.
        :param timeout: Connection timeout in seconds.
        :param chunk_size: Size of the chunks in bytes.
        :param api: sbApi instance.
        """
        threading.Thread.__init__(self)
        if not url:
            raise SbgError('Url must be supplied.')
        if not file_path:
            raise SbgError('File path must be supplied.')

        if api is None:
            raise SbgError('Api instance not supplied.')

        if chunk_size and chunk_size < PartSize.MINIMUM_PART_SIZE:
            raise SbgError(
                message='Chunk size is too small! Minimum chunk size is %s'
                        % PartSize.MINIMUM_PART_SIZE
            )
        self._session = requests.Session()
        self.url = url
        self._file_path = file_path
        self._temp_file = self._file_path + '.' + hashlib.sha1(
            self._file_path.encode('utf-8')).hexdigest()[:10]
        self._retry = retry
        self._timeout = timeout
        if chunk_size:
            self._chunk_size = chunk_size
        else:
            self._chunk_size = PartSize.DOWNLOAD_MINIMUM_PART_SIZE
        self._api = api
        self._bytes_done = 0
        self._running = threading.Event()
        self._callback = None
        self._errorback = None
        self._progress_callback = None
        self._time_started = 0
        try:
            self._file_size = self._get_file_size()
        except SbgError as error:
            if self._errorback:
                self._errorback(error)
            else:
                raise error
        self._status = TransferState.NOT_INITIALIZED
        self._stop_signal = False

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
        self._callback = callback
        self._errorback = errorback

    def add_progress_callback(self, callback=None):
        self._progress_callback = callback

    def pause(self):
        self._running.clear()
        self._status = TransferState.PAUSED

    def stop(self):
        self._stop_signal = True
        self.join()
        self._status = TransferState.STOPPED
        if self._callback:
            return self._callback(self._status)

    def resume(self):
        self._running.set()
        self._status = TransferState.RUNNING

    def wait(self):
        if self._status != TransferState.NOT_INITIALIZED:
            self._status = TransferState.COMPLETED
            self.join()

    def run(self):
        self._running.set()
        self._status = TransferState.RUNNING
        self._time_started = time.time()

        chunked_file = ChunkedFile(self._temp_file,
                                   self._session,
                                   self.url,
                                   self._file_size,
                                   self._chunk_size,
                                   self._retry,
                                   self._timeout,
                                   self._api.download_pool)

        try:
            for chunk in chunked_file:
                if self._stop_signal:
                    return
                self._running.wait()
                self._bytes_done += chunk.size
                if self._progress_callback:
                    progress = Progress(
                        chunked_file.total, chunked_file.total_submitted,
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
        try:
            response = requests.get(
                self.url, timeout=self._timeout, stream=True
            )
        except requests.RequestException as e:
            if self._errorback:
                return self._errorback(SbgError(str(e)))
            else:
                raise SbgError(str(e))

        file_size = response.headers.get('Content-Length', None)
        if not file_size:
            raise SbgError('Server did not provide Content-Length Headers!')

        if int(file_size) == 0:
            raise SbgError('File size is 0. Refusing to download.')

        return int(file_size)
