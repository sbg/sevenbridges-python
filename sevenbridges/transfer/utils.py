import sys


class PartSize(object):
    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB
    TB = 1024 * GB
    MINIMUM_PART_SIZE = 5 * MB
    MAXIMUM_UPLOAD_SIZE = 5 * GB
    MAXIMUM_OBJECT_SIZE = 5 * TB
    MAXIMUM_TOTAL_PARTS = 10000

    DOWNLOAD_MINIMUM_PART_SIZE = 64 * MB


class TransferState(object):
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    COMPLETED = 'COMPLETED'
    NOT_INITIALIZED = 'NOT INITIALIZED'
    STOPPED = 'STOPPED'


class Chunk(object):
    def __init__(self, start=None, size=None):
        self._start = start
        self._size = size

    @property
    def start(self):
        return self._start

    @property
    def size(self):
        return self._size


class Progress(object):
    def __init__(self, num_of_chunks, chunks_done, bytes_done,
                 file_size, duration):
        self._num_of_chunks = num_of_chunks
        self._chunks_done = chunks_done
        self._bytes_done = bytes_done
        self._file_size = file_size
        self._duration = duration

    @property
    def num_of_chunks(self):
        return self._num_of_chunks

    @property
    def chunks_done(self):
        return self._chunks_done

    @property
    def bytes_done(self):
        return self._bytes_done

    @property
    def file_size(self):
        return self._file_size

    @property
    def duration(self):
        return self._duration

    @property
    def progress(self):
        progress = (self._bytes_done / self._file_size) * 100
        if progress > 100:
            progress = 100.0
        return progress

    @property
    def bandwidth(self):
        return (self._bytes_done / 1000000) / self.duration


def simple_progress_bar(progress):
    sys.stdout.write(
        '\rTransfer: Progress[%.2f%%], Bandwidth[%.2fMB/s], Chunks[total=%s, '
        'Done=%s],  Duration[%.2fs]\b' % (
            progress.progress, progress.bandwidth, progress.num_of_chunks,
            progress.chunks_done, progress.duration))
    sys.stdout.flush()
