from datetime import datetime

import faker
import pytest

from sevenbridges.errors import SbgError

generator = faker.Factory.create()


@pytest.mark.parametrize("parent", [generator.uuid4(), None])
def test_tasks_query(api, given, verifier, parent):
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.task.tasks_in_project_for_parent(id, parent, total)

    # action
    projects = api.tasks.query(project=id)

    # verification
    assert projects.total == total
    assert len(projects) == total

    verifier.task.tasks_for_project_fetched(id)


def test_tasks_query_dates(api, given, verifier):
    test_date = datetime(2017, 1, 10, 14, 4, 23, 838459)
    test_datestring = '2017-01-10T14:04:23'
    # preconditions
    total = 10
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.task.tasks_in_project(id, total)

    # action
    tasks = api.tasks.query(project=id, created_from=test_date,
                            created_to=test_date,
                            started_from=test_date, started_to=test_date,
                            ended_from=test_date, ended_to=test_date)

    # verification
    assert tasks.total == total
    assert len(tasks) == total

    verifier.task.tasks_with_dates_fetched(id, test_datestring)


def test_task_get_batch_children(api, given, verifier):
    # preconditions
    parent_id = generator.uuid4()
    total = 2
    given.task.task_exists(id=parent_id, status='RUNNING', batch=True)
    given.task.tasks_exist_for_parent(parent_id, total)

    # actions
    task = api.tasks.get(parent_id)
    children = task.get_batch_children()

    # verification
    assert len(children) == total
    verifier.task.task_fetched(parent_id)
    verifier.task.task_children_fetched(parent_id)


@pytest.mark.parametrize("run", [True, False])
def test_create_task(api, given, verifier, run):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    project_id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=project_id)
    given.file.files_exist_for_project(project_id, 10)
    app_id = '{}/{}/{}'.format(owner, project_short_name, 'app-name')
    batch_by = {'type': 'item'}

    project = api.projects.get(id=project_id)
    files = api.files.query(project=project)
    inputs = {'FastQC': files, 'reads': False, 'some_file': files[0]}
    given.task.can_be_created(
        batch_by=batch_by, batch_input='FastQC', app=app_id, project=project.id
    )
    # action
    task = api.tasks.create(
        generator.name(), project, app_id, batch_input='FastQC',
        batch_by=batch_by, inputs=inputs, run=run
    )

    # verification
    assert repr(task)
    verifier.task.task_created()


@pytest.mark.parametrize("run", [True, False])
def test_create_task_with_errors(api, given, verifier, run):
    # preconditions
    owner = generator.user_name()
    project_short_name = generator.slug()
    project_id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=project_id)
    given.file.files_exist_for_project(project_id, 10)
    app_id = '{}/{}/{}'.format(owner, project_short_name, 'app-name')
    batch_by = {'type': 'item'}

    project = api.projects.get(id=project_id)
    files = api.files.query(project=project)
    inputs = {'FastQC': files, 'reads': False, 'some_file': files[0]}
    given.task.created_with_errors(
        batch_by=batch_by, batch_input='FastQC', app=app_id, project=project.id
    )
    # action
    if run:
        with pytest.raises(SbgError):
            task = api.tasks.create(
                generator.name(), project, app_id, batch_input='FastQC',
                batch_by=batch_by, inputs=inputs, run=run
            )
    else:
        task = api.tasks.create(
            generator.name(), project, app_id, batch_input='FastQC',
            batch_by=batch_by, inputs=inputs, run=run
        )
        assert repr(task)
        verifier.task.task_created()


def test_abort_task(api, given, verifier):
    # precondition
    id = generator.uuid4()
    given.task.task_exists(id=id, status='RUNNING')
    given.task.task_can_be_aborted(id=id, status='ABORTED')
    # action
    task = api.tasks.get(id)
    task.abort()

    # verification
    assert task.status == 'ABORTED'
    verifier.task.action_performed(id, 'abort')


@pytest.mark.parametrize("batch", [True, False])
@pytest.mark.parametrize("inplace", [True, False])
def test_run_task(api, given, batch, inplace, verifier):
    # precondition
    id = generator.uuid4()
    given.task.task_exists(id=id, status='DRAFT')
    given.task.task_can_be_run(id=id, status='RUNNING')

    # action
    task = api.tasks.get(id)
    task.run(batch=batch, inplace=inplace)

    # verification
    if inplace:
        assert task.status == 'RUNNING'
        verifier.task.action_performed(id, 'run')
    else:
        assert task.status == 'DRAFT'
        verifier.task.action_performed(id, 'run')


def test_save_task(api, given, verifier):
    # precondition
    owner = generator.user_name()
    project_short_name = generator.slug()
    project_id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=project_id)
    given.file.files_exist_for_project(project_id, 10)
    id = generator.uuid4()
    given.task.task_exists(id=id)
    given.task.task_can_be_saved(id=id, status='DRAFT')

    # action
    project = api.projects.get(id=project_id)
    files = project.get_files(limit=10)
    task = api.tasks.get(id)
    task.name = generator.name()
    task.description = generator.name()
    task.inputs = {'test': files, 'test1': files[0], 'test2': 'test'}
    task.save()
    assert task.status == 'DRAFT'
    # verification
    verifier.task.task_saved(id)

    files.append(files[0])
    task.inputs = {'test': files, 'test1': files[0], 'test2': 'test'}
    task.save()
    assert task.status == 'DRAFT'
    # verification
    verifier.task.task_saved(id)


def test_get_execution_details(api, given, verifier):
    # precondition
    id = generator.uuid4()
    given.task.task_exists(id=id)
    given.task.task_execution_details_exist(id=id)

    # action
    task = api.tasks.get(id=id)
    task.get_execution_details()

    # verification
    verifier.task.execution_details_fetched(id=id)


def test_raw_response(api, given, verifier):
    # precondition
    id = generator.uuid4()
    given.task.task_exists(id=id)

    # action
    task = api.tasks.get(id=id)

    # verification
    verifier.task.task_fetched(id=id)
    assert isinstance(task.raw, dict)
    assert {'app', 'href', 'id', 'inputs'} <= set(task.raw.keys())
