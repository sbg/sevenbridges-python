import sys

import math


class Part(object):
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
    def __init__(self, num_of_parts, parts_done, bytes_done,
                 file_size, duration):
        self._num_of_parts = num_of_parts
        self._parts_done = parts_done
        self._bytes_done = bytes_done
        self._file_size = file_size
        self._duration = duration

    @property
    def num_of_parts(self):
        return self._num_of_parts

    @property
    def parts_done(self):
        return self._parts_done

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
        progress = (self._bytes_done / float(self._file_size)) * 100
        progress = progress if progress <= 100 else 100
        return progress

    @property
    def bandwidth(self):
        return (self._bytes_done / 1000000) / self.duration


def total_parts(file_size, part_size):
    return int(math.ceil(file_size / float(part_size)))


def simple_progress_bar(progress):
    sys.stdout.write(
        '\rTransfer: Progress[%.2f%%], Bandwidth[%.2fMB/s], Parts[total=%s, '
        'Done=%s],  Duration[%.2fs]\b' % (
            progress.progress, progress.bandwidth, progress.num_of_parts,
            progress.parts_done, progress.duration
        )
    )
    sys.stdout.flush()
