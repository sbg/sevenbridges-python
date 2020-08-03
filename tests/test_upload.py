import os
import faker
import pytest
import tempfile

from sevenbridges.errors import SbgError
from sevenbridges.models.enums import PartSize
from sevenbridges.transfer.upload import Upload

generator = faker.Factory.create()


@pytest.mark.parametrize("path", [generator.uuid4(), None])
def test_file_upload_wrong_path(api, path):
    project_id = generator.uuid4()
    file_name = generator.uuid4()

    with pytest.raises(SbgError):
        Upload(
            path,
            project=project_id,
            api=api,
            part_size=1,
            file_name=file_name
        )


@pytest.mark.parametrize("empty_file", [True, False])
@pytest.mark.parametrize("project_id", [generator.uuid4(), None])
@pytest.mark.parametrize("parent_id", [generator.uuid4(), None])
@pytest.mark.parametrize("no_api", [True, False])
def test_file_upload(api, given, empty_file, project_id, parent_id, no_api):
    upload_id = generator.uuid4()
    api_instance = api
    file_id = generator.uuid4()
    file_part_url = generator.url()
    file_content = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.finalized_upload(file_id)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    if not empty_file:
        temp_file.write(file_content)
    temp_file.close()

    project_and_parent = project_id is not None and parent_id is not None
    no_project_or_parent = project_id is None and parent_id is None
    if no_api:
        api_instance = None
    if project_and_parent or no_project_or_parent or no_api:
        with pytest.raises(SbgError):
            Upload(
                temp_file.name,
                project=project_id,
                parent=parent_id,
                api=api_instance,
                part_size=1
            )
    else:
        upload = Upload(
            temp_file.name,
            project=project_id,
            parent=parent_id,
            api=api,
            part_size=1
        )
        upload.start()
        upload.wait()
        result = upload.result()

        assert upload.status == 'COMPLETED'
        assert result.id == file_id
        assert upload.duration > 0
        assert upload.file_name == os.path.basename(temp_file.name)
        assert upload.start_time > 0

    os.remove(temp_file.name)


def test_file_upload_init_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=1, upload_id=upload_id, failed=True
    )

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')

    temp_file.write('dummy content')
    temp_file.close()
    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()

    os.remove(temp_file.name)


def test_file_upload_start_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=1, upload_id=upload_id, failed=True
    )
    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')

    temp_file.write('dummy content')
    temp_file.close()
    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload._status = 'RUNNING'
    with pytest.raises(SbgError):
        upload.start()

    os.remove(temp_file.name)


def test_file_upload_finalize_failed(api, given):
    upload_id = generator.uuid4()
    file_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.finalized_upload(file_id, failed=True)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')

    temp_file.write('dummy content')
    temp_file.close()
    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()

    os.remove(temp_file.name)


def test_file_upload_part_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url, failed=True)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')

    temp_file.write('dummy content')
    temp_file.close()
    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()

    os.remove(temp_file.name)


def test_file_upload_etag_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url, failed=True)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')

    temp_file.write('dummy content')
    temp_file.close()
    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()

    os.remove(temp_file.name)


def test_file_upload_report_part_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part(failed=True)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')

    temp_file.write('dummy content')
    temp_file.close()
    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()

    os.remove(temp_file.name)


def test_file_upload_stop(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'RUNNING'
    upload.stop()
    os.remove(temp_file.name)

    assert upload.status == 'STOPPED'


def test_file_upload_stop_failed(api, given, ):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'STOPPED'
    with pytest.raises(SbgError):
        upload.stop()
    os.remove(temp_file.name)


def test_file_upload_abort_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted(failed=True)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    with pytest.raises(SbgError):
        upload.stop()
    os.remove(temp_file.name)


def test_file_upload_pause(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'RUNNING'
    upload.pause()
    os.remove(temp_file.name)

    assert upload.status == 'PAUSED'


def test_file_upload_pause_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'STOPPED'
    with pytest.raises(SbgError):
        upload.pause()
    os.remove(temp_file.name)


def test_file_upload_resume(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'PAUSED'
    upload.resume()
    os.remove(temp_file.name)

    assert upload.status == 'RUNNING'


def test_file_upload_resume_failed(api, given):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'RUNNING'
    with pytest.raises(SbgError):
        upload.resume()
    os.remove(temp_file.name)


def test_file_size_too_large(api, monkeypatch):
    project_id = generator.uuid4()
    file_name = generator.uuid4()
    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()
    with monkeypatch.context() as m:
        m.setattr(
            "os.path.getsize",
            lambda x: PartSize.MAXIMUM_OBJECT_SIZE + 1
        )

        with pytest.raises(SbgError):
            Upload(
                temp_file.name,
                project_id,
                api=api,
                part_size=1,
                file_name=file_name
            )
    os.remove(temp_file.name)
