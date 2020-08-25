from sevenbridges.transfer.utils import Part, Progress


def test_transfer_utils():
    start = 10
    size = 20
    part = Part(start=start, size=size)
    assert part.start == start and part.size == size

    num_of_parts = 10
    parts_done = 2
    bytes_done = 2000000
    file_size = 10
    duration = 2
    p = Progress(num_of_parts, parts_done, bytes_done, file_size, duration)

    assert p.num_of_parts == num_of_parts
    assert p.file_size == file_size
    assert p.duration == duration
    assert p.bytes_done == bytes_done
    assert p.bandwidth == 1
    assert p.progress > 0
