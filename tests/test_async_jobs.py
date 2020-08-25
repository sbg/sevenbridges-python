import faker
import pytest

from sevenbridges.models.async_jobs import AsyncFileBulkRecord
from sevenbridges.models.enums import AsyncFileOperations, AsyncJobStates

generator = faker.Factory.create()


def test_list_file_jobs(api, given, verifier):
    # preconditions
    total = 10
    given.async_jobs.list_file_jobs(total)

    # action
    jobs = api.async_jobs.list_file_jobs()

    # verification
    assert len(jobs) == total
    verifier.async_jobs.listed()


def test_get_copy_files_job(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    given.async_jobs.exists(id=id, type=AsyncFileOperations.COPY)

    # action
    job = api.async_jobs.get_file_copy_job(id=id)

    # verification
    assert job.id == id
    verifier.async_jobs.file_copy_job_fetched(id=id)


def test_get_move_files_job(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    given.async_jobs.exists(id=id, type=AsyncFileOperations.MOVE)

    # action
    job = api.async_jobs.get_file_move_job(id=id)

    # verification
    assert job.id == id
    verifier.async_jobs.file_move_job_fetched(id=id)


def test_get_delete_files_job(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    given.async_jobs.exists(id=id, type=AsyncFileOperations.DELETE)

    # action
    job = api.async_jobs.get_file_delete_job(id=id)

    # verification
    assert job.id == id
    verifier.async_jobs.file_delete_job_fetched(id=id)


def test_get_results(api, given, verifier):
    # preconditions
    id = generator.uuid4()

    expected_result = [
        {'resource': {'id': generator.uuid4()}},
        {'error': {'status': 404}},
    ]
    given.async_jobs.exists(
        id=id,
        result=expected_result,
        type=AsyncFileOperations.COPY,
    )

    # action
    job = api.async_jobs.get_file_copy_job(id=id)
    result = job.get_result()

    # verification
    verifier.async_jobs.file_copy_job_fetched(id=id)
    assert all(isinstance(r, AsyncFileBulkRecord) for r in result)
    assert len(result) == 2
    assert result[0].valid
    assert not result[1].valid


@pytest.mark.parametrize("location", ['parent', 'project'])
def test_async_copy_files(api, given, verifier, location):
    # preconditions
    total = 10
    files = [
        {
            'file': generator.uuid4(),
            'location': generator.uuid4(),
            'name': generator.slug()
        } for _ in range(total)
    ]
    given.async_jobs.can_copy_files(files=files)

    # action
    job = api.async_jobs.file_bulk_copy(files=files)

    # verification
    assert job.state == AsyncJobStates.SUBMITTED
    assert len(job.result) == total
    verifier.async_jobs.async_files_copied()


@pytest.mark.parametrize("location", ['parent', 'project'])
def test_async_move_files(api, given, verifier, location):
    # preconditions
    total = 10
    files = [
        {
            'file': generator.uuid4(),
            'location': generator.uuid4(),
            'name': generator.slug()
        } for _ in range(total)
    ]
    given.async_jobs.can_move_files(files=files)

    # action
    job = api.async_jobs.file_bulk_move(files=files)

    # verification
    assert job.state == AsyncJobStates.SUBMITTED
    assert len(job.result) == total
    verifier.async_jobs.async_files_moved()


def test_async_delete_files(api, given, verifier):
    # preconditions
    total = 10
    files = [
        {
            'file': generator.uuid4(),
        } for _id in range(total)
    ]
    given.async_jobs.can_delete_files(files=files)

    # action
    job = api.async_jobs.file_bulk_delete(files=files)

    # verification
    assert job.state == AsyncJobStates.SUBMITTED
    assert len(job.result) == total
    verifier.async_jobs.async_files_deleted()
