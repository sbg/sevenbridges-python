import os

import faker
import pytest
import six

from sevenbridges.errors import SbgError
from sevenbridges.models.enums import PartSize, TransferState
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
            part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
            file_name=file_name
        )


@pytest.mark.parametrize("empty_file", [True, False])
@pytest.mark.parametrize("project_id", [generator.uuid4(), None])
@pytest.mark.parametrize("parent_id", [generator.uuid4(), None])
@pytest.mark.parametrize("no_api", [True, False])
def test_file_upload(api, given, empty_file, project_id, parent_id, no_api,
                     tmpdir):
    upload_id = generator.uuid4()
    api_instance = api
    file_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    file_content = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.finalized_upload(file_id)

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        if not empty_file:
            temp_file.write(str(file_content))

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
                part_size=PartSize.UPLOAD_RECOMMENDED_SIZE
            )
    else:
        upload = Upload(
            temp_file.name,
            project=project_id,
            parent=parent_id,
            api=api,
            part_size=PartSize.UPLOAD_RECOMMENDED_SIZE
        )
        upload.start()
        upload.wait()
        result = upload.result()

        assert upload.status == TransferState.COMPLETED
        assert result.id == file_id
        assert upload.duration > 0
        assert upload.file_name == os.path.basename(temp_file.name)
        assert upload.start_time > 0


def test_file_upload_init_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id,
        failed=True
    )

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()


def test_file_upload_start_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id,
        failed=True
    )

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload._status = TransferState.RUNNING
    with pytest.raises(SbgError):
        upload.start()


def test_file_upload_finalize_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    file_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.finalized_upload(file_id, failed=True)

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()


def test_file_upload_part_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url, failed=True)

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()


def test_file_upload_etag_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url, failed=True)
    given.uploads.got_etag(file_part_url, failed=True)

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )

    with pytest.raises(SbgError):
        upload.run()


def test_file_upload_stop(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload.start()
    upload._status = TransferState.RUNNING
    upload.stop()

    assert upload.status == TransferState.STOPPED


def test_file_upload_stop_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    with pytest.raises(SbgError):
        upload.stop()


def test_file_upload_abort_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted(failed=True)

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload.start()
    with pytest.raises(SbgError):
        upload.stop()


def test_file_upload_pause(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()

    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload.start()
    upload._status = TransferState.RUNNING
    upload.pause()

    assert upload.status == TransferState.PAUSED
    upload.stop()


def test_file_upload_pause_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload._status = TransferState.STOPPED
    with pytest.raises(SbgError):
        upload.pause()


def test_file_upload_resume(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()
    given.uploads.deleted()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload.start()
    upload._status = TransferState.RUNNING
    upload.pause()
    upload._status = TransferState.PAUSED
    upload.resume()

    assert upload.status == TransferState.RUNNING
    upload.stop()


def test_file_upload_resume_failed(api, given, tmpdir):
    upload_id = generator.uuid4()
    project_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.uploads.initialized_upload(
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE, upload_id=upload_id
    )
    given.uploads.got_file_part(file_part_url)
    given.uploads.got_etag(file_part_url)
    given.uploads.reported_part()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

    upload = Upload(
        temp_file.name,
        project_id,
        api=api,
        part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
        file_name=file_name
    )
    upload._status = TransferState.RUNNING
    with pytest.raises(SbgError):
        upload.resume()


def test_file_size_too_large(api, monkeypatch, tmpdir):
    project_id = generator.uuid4()
    file_name = generator.uuid4()

    with open(six.text_type(tmpdir / file_name), 'w') as temp_file:
        temp_file.write('dummy content')

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
                part_size=PartSize.UPLOAD_RECOMMENDED_SIZE,
                file_name=file_name
            )
