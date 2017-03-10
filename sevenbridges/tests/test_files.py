import faker
import pytest

from sevenbridges.errors import SbgError

generator = faker.Factory.create()


def test_files_query(api, given, verifier):
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.file.files_exist_for_project(id, 10)
    given.project.exists(id=id)

    # action
    project = api.projects.get(id)
    projects = api.files.query(project=project, limit=total)

    # verification
    assert projects.total == total
    assert len(projects) == total

    verifier.file.queried(project=project.id)


def test_files_query_file_name(api, given, verifier):
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    file_name = ''.join(generator.name().split())
    given.file.files_exist_for_file_name(id, file_name, 10)
    given.project.exists(id=id)

    # action
    project = api.projects.get(id)
    projects = api.files.query(project=id, names=[file_name], limit=10)

    # verification
    assert projects.total == total
    assert len(projects) == total

    verifier.file.queried_with_file_name(id, file_name)


def test_files_query_file_metadata(api, given, verifier):
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    key = 'key'
    value = 'value'
    given.file.files_exist_for_file_metadata(id, key, value, 10)
    given.project.exists(id=id)

    # action
    project = api.projects.get(id)
    projects = api.files.query(project=id, metadata={key: value}, limit=10)

    # verification
    assert projects.total == total
    assert len(projects) == total

    verifier.file.queried_with_file_metadata(id, key, value)


def test_files_query_file_origin(api, given, verifier):
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    key = 'key'
    value = 'value'
    given.file.files_exist_for_file_origin(id, key, value, 10)
    given.project.exists(id=id)

    # action
    _ = api.projects.get(id)
    projects = api.files.query(project=id, origin={key: value}, limit=10)

    # verification
    assert projects.total == total
    assert len(projects) == total

    verifier.file.queried_with_file_origin(id, key, value)


def test_files_query_tags(api, given, verifier):
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    tags = ['test1', 'test2']
    given.file.files_exist_for_file_tag(id, tags, 10)
    given.project.exists(id=id)

    # action
    _ = api.projects.get(id)
    projects = api.files.query(project=id, tags=tags, limit=10)

    # verification
    assert projects.total == total
    assert len(projects) == total

    verifier.file.queried_with_file_tags(id, tags)


def test_files_copy(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    new_id = generator.uuid4()
    given.file.exists(id=id)
    given.file.can_be_copied(id=id, new_id=new_id)

    # action
    file = api.files.get(id)
    new_file = file.copy('test-project', 'test-file')

    assert new_file.id == new_id
    assert 'id' in repr(new_file)
    verifier.file.file_copied(id)


def test_files_download_info(api, given, verifier):
    # precondition
    id = generator.uuid4()
    given.file.exists(id=id)
    given.file.download_info_defined(id=id)

    # action
    file = api.files.get(id)
    info = file.download_info()

    assert info.url is not None
    assert 'url' in repr(info)

    verifier.file.download_info_fetched(id)


def test_files_save(api, given, verifier):
    # precondition
    id = generator.uuid4()
    given.file.exists(id=id)
    given.file.can_be_saved(id=id)
    new_sample_value = generator.name()
    given.file.metadata_can_be_saved(id)
    # action
    file = api.files.get(id)
    file.metadata['sample'] = new_sample_value
    file.save()

    # verifier
    verifier.file.file_saved(id)


@pytest.mark.parametrize("tags", [['test'], ['test', 'test2']])
def test_files_save_tags(api, given, verifier, tags):
    # precondition
    id = generator.uuid4()
    given.file.exists(id=id, tags=['test'])

    given.file.can_be_saved(id=id)
    given.file.metadata_can_be_saved(id)
    given.file.tags_can_be_saved(id)
    # action
    file = api.files.get(id)
    file.tags = tags
    if len(tags) == 1:
        with pytest.raises(SbgError):
            file.save()
        return
    else:
        file.save()
    verifier.file.file_saved_tags(id)
