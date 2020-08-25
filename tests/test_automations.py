import faker
import pytest
import tempfile
import os

from sevenbridges.errors import SbgError
from sevenbridges.transfer.upload import CodePackageUpload

generator = faker.Factory.create()


def test_get_automation(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()

    given.automations.exists(id=id)

    # action
    automation = api.automations.get(id=id)

    # verification
    assert automation.id == id
    verifier.automations.fetched(id=id)


@pytest.mark.parametrize("name", [generator.name(), None])
def test_create_automation(api, given, verifier, name):
    # preconditions
    automation_description = generator.name()
    billing_group = generator.uuid4()
    settings = {
        "secret_token": generator.uuid4()
    }

    given.automations.can_be_created(
        name=name,
        billing_group=billing_group,
        description=automation_description,
        secret_settings=settings
    )

    # action
    if name:
        automation = api.automations.create(
            name=name, billing_group=billing_group,
            description=automation_description,
            secret_settings=settings
        )

        # verification
        assert automation.name == name
        assert automation.description == automation_description
        assert automation.billing_group == billing_group
        assert set(automation.secret_settings).issubset(set(settings))

        verifier.automations.created()
    else:
        with pytest.raises(SbgError):
            api.automations.create(
                name=name, billing_group=billing_group,
                description=automation_description
            )


@pytest.mark.parametrize("project_based", [True, False])
def test_create_project_based_automation(api, given, project_based):
    # preconditions
    name = generator.name()
    given.automations.can_be_created(name=name, project_based=project_based)

    # action
    automation = api.automations.create(name, project_based=project_based)

    # verification
    assert automation.project_based == project_based


def test_modify_automation(api, given, verifier):
    # preconditions
    automation_id = generator.uuid4()
    given.automations.exists(id=automation_id)
    new_name = generator.name()
    new_billing_group = generator.uuid4()
    given.automations.can_be_saved(
        id=automation_id, name=new_name, billing_group=new_billing_group
    )

    # action
    automation = api.automations.get(automation_id)

    # verification
    automation.name = new_name
    automation.billing_group = new_billing_group
    automation.save()
    assert automation.name == new_name
    assert automation.billing_group == new_billing_group

    verifier.automations.saved(id=automation.id)


def test_archive_automation(api, given, verifier):
    # preconditions
    automation_id = generator.uuid4()
    given.automations.exists(id=automation_id)
    given.automations.can_be_archived(id=automation_id)

    # action
    automation = api.automations.get(automation_id)
    automation.archive()

    assert automation.archived

    # verification
    verifier.automations.action_archive_performed(id=automation.id)


def test_restore_automation(api, given, verifier):
    # preconditions
    automation_id = generator.uuid4()
    given.automations.exists(id=automation_id)
    given.automations.can_be_restored(id=automation_id)

    # action
    automation = api.automations.get(automation_id)
    automation.restore()

    assert not automation.archived

    # verification
    verifier.automations.action_restore_performed(id=automation.id)


def test_query_automations(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    name = generator.slug()
    given.automations.query(total)

    # action
    automations = api.automations.query(name=name)

    # verification
    assert len(automations) == total

    verifier.automations.queried(name=name)


def test_get_packages(api, given, verifier):
    # precondition
    api.aa = True
    total = 10

    id = generator.uuid4()
    given.automations.exists(id=id)
    given.automations.has_packages(id, total)

    # action
    automation = api.automations.get(id)
    members = automation.get_packages()

    # verification
    assert len(members) == total
    verifier.automations.packages_retrieved(id)


def test_get_package(api, given, verifier):
    # precondition
    api.aa = True
    package_id = generator.uuid4()
    given.automations.has_package(package_id)

    # action
    package = api.automations.get_package(package_id)

    # verification
    assert package.id == package_id
    verifier.automations.package_retrieved(package_id)


@pytest.mark.parametrize("file", [True, False])
@pytest.mark.parametrize("version", [generator.slug(), None])
@pytest.mark.parametrize("schema", [{"test": "test"}, None])
def test_add_package(api, given, verifier, file, version, schema):
    # preconditions
    automation_id = generator.uuid4()
    package_id = generator.uuid4()
    package_file_id = generator.uuid4()
    upload_id = generator.uuid4()
    file_part_url = generator.url()
    given.automations.exists(id=automation_id)
    given.automations.can_add_package(
        package_id=package_id, automation_id=automation_id,
        location=package_file_id, version=version, schema=schema
    )
    given.cp_uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.cp_uploads.got_file_part(file_part_url)
    given.cp_uploads.got_etag(file_part_url)
    given.cp_uploads.reported_part()
    given.cp_uploads.finalized_upload(package_file_id)

    automation = api.automations.get(automation_id)

    # action
    if file and version and schema:
        temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
        temp_file.write('dummy content')
        temp_file.close()

        package = automation.add_package(
            file_path=temp_file.name, version=version, schema=schema
        )
        os.remove(temp_file.name)
        # verification
        assert package.location == package_file_id
        assert package.version == version

        verifier.automation_packages.created(automation_id=automation_id)
    else:
        with pytest.raises(SbgError):
            automation.add_package(
                file_path=None, version=version,
                schema=schema
            )


@pytest.mark.parametrize("empty_file", [True, False])
def test_code_package_upload(api, given, empty_file):
    upload_id = generator.uuid4()
    automation_id = generator.uuid4()
    file_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.cp_uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.cp_uploads.got_file_part(file_part_url)
    given.cp_uploads.got_etag(file_part_url)
    given.cp_uploads.reported_part()
    given.cp_uploads.finalized_upload(file_id)

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    if not empty_file:
        temp_file.write('dummy content')
    temp_file.close()

    if empty_file:
        with pytest.raises(SbgError):
            CodePackageUpload(
                temp_file.name,
                automation_id,
                api=api,
                part_size=1,
                file_name=file_name
            )
    else:
        upload = CodePackageUpload(
            temp_file.name,
            automation_id,
            api=api,
            part_size=1,
            file_name=file_name
        )
        upload.start()
        upload.wait()
        result = upload.result()

        assert upload.status == 'COMPLETED'
        assert result.id == file_id
    os.remove(temp_file.name)


def test_code_package_upload_stop(api, given):
    upload_id = generator.uuid4()
    automation_id = generator.uuid4()
    file_part_url = generator.url()
    file_name = generator.uuid4()
    given.cp_uploads.initialized_upload(part_size=1, upload_id=upload_id)
    given.cp_uploads.got_file_part(file_part_url)
    given.cp_uploads.got_etag(file_part_url)
    given.cp_uploads.reported_part()
    given.cp_uploads.deleted()

    temp_file = tempfile.NamedTemporaryFile('w', delete=False, dir='/tmp')
    temp_file.write('dummy content')
    temp_file.close()

    upload = CodePackageUpload(
        temp_file.name,
        automation_id,
        api=api,
        part_size=1,
        file_name=file_name
    )
    upload.start()
    upload._status = 'RUNNING'
    upload.stop()
    os.remove(temp_file.name)

    assert upload.status == 'STOPPED'


def test_archive_package(api, given, verifier):
    # preconditions
    automation_id = generator.uuid4()
    package_id = generator.uuid4()
    given.automation_packages.exists(
        id=package_id, automation=automation_id
    )
    given.automation_packages.can_be_archived(
        id=package_id, automation=automation_id
    )

    # action
    package = api.automations.get_package(package_id)
    package.archive()

    assert package.archived

    # verification
    verifier.automation_packages.action_archive_performed(
        automation_id=automation_id, package_id=package_id
    )


def test_modify_package(api, given, verifier):
    # preconditions
    automation_id = generator.uuid4()
    package_id = generator.uuid4()
    new_custom_url = generator.url()
    given.automation_packages.exists(
        id=package_id, automation=automation_id
    )
    given.automation_packages.can_be_saved(
        id=package_id, automation=automation_id, custom_url=new_custom_url
    )

    # action
    package = api.automation_packages.get(package_id)
    package.custom_url = new_custom_url
    package.save()

    assert package.custom_url == new_custom_url

    # verification
    verifier.automation_packages.saved(id=package_id)


def test_restore_package(api, given, verifier):
    # preconditions
    automation_id = generator.uuid4()
    package_id = generator.uuid4()
    given.automation_packages.exists(
        id=package_id, automation=automation_id
    )
    given.automation_packages.can_be_restored(
        id=package_id, automation=automation_id
    )

    # action
    package = api.automations.get_package(package_id)
    package.restore()

    assert not package.archived

    # verification
    verifier.automation_packages.action_restore_performed(
        automation_id=automation_id, package_id=package_id
    )


def test_get_member(api, given, verifier):
    # precondition
    api.aa = True
    member_username = generator.user_name()
    id = generator.uuid4()
    given.automations.exists(id=id)
    given.automations.has_member(id, member_username)

    # action
    automation = api.automations.get(id)
    member = automation.get_member(member_username)

    # verification
    assert member.username == member_username
    verifier.automations.member_retrieved(id, member_username)


def test_get_members(api, given, verifier):
    # precondition
    api.aa = True
    total = 10

    id = generator.uuid4()
    given.automations.exists(id=id)
    given.automations.has_members(id, total)

    # action
    automation = api.automations.get(id)
    packages = automation.get_members()

    # verification
    assert len(packages) == total
    verifier.automations.members_retrieved(id)


def test_add_member(api, given, verifier):
    # precondition
    api.aa = True
    username = generator.user_name()
    permissions = {
        "write": True,
        "read": True,
        "copy": True,
        "execute": True,
        "admin": True
    }
    id = generator.uuid4()

    given.automations.exists(id=id)
    given.automations.can_add_member(id, username)

    # action
    automation = api.automations.get(id)
    automation.add_member(username, permissions)

    # verification
    verifier.automations.member_added(id)


def test_remove_member(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()
    username = generator.user_name()

    given.automations.exists(id=id)
    given.automations.has_member(id, username)
    given.automations.can_remove_member(id, username)

    # action
    automation = api.automations.get(id)
    automation.remove_member(username)

    # verification
    verifier.automations.member_removed(id, username)


def test_save_member(api, given, verifier):
    # precondition
    api.aa = True

    id = generator.uuid4()
    username = generator.user_name()

    given.automations.exists(id=id)
    given.automations.has_member(id=id, username=username)
    given.automation_members.exists(username=username, automation=id)
    given.automation_members.can_be_saved(username=username, automation=id)

    # # action
    automation = api.automations.get(id=id)
    member = automation.get_member(username=username)
    member.permissions['admin'] = True
    member.save()

    # # verification
    verifier.automation_members.saved(automation=id, username=username)


def test_get_runs(api, given, verifier):
    # precondition
    api.aa = True
    total = 10
    name = generator.name()

    id = generator.uuid4()
    given.automations.exists(id=id)
    given.automations.has_runs(id, total)

    # action
    automation = api.automations.get(id)
    runs = automation.get_runs(name=name)

    # verification
    assert len(runs) == total
    verifier.automations.runs_retrieved()


def test_get_run(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()

    given.automation_runs.exists(id=id)

    # action
    automation_run = api.automation_runs.get(id=id)

    # verification
    assert automation_run.id == id
    verifier.automation_runs.fetched(id=id)


def test_query_runs(api, given, verifier):
    # precondition
    api.aa = True
    total = 10
    name = generator.name()
    given.automation_runs.query(total=total)

    # action
    automation_runs = api.automation_runs.query(name=name)

    # verification
    assert len(automation_runs) == total
    verifier.automation_runs.queried(name=name)


def test_create_run(api, given, verifier):
    # precondition
    api.aa = True

    inputs = {}
    name = generator.name()
    id = generator.uuid4()
    secret_settings = {generator.name(): generator.name()}
    given.automations.exists(id=id)
    given.automations.has_packages(id=id, total=1)
    given.automation_runs.can_be_created()

    # action
    automation = api.automations.get(id=id)
    package = automation.get_packages()[0]
    api.automation_runs.create(
        package=package,
        inputs=inputs,
        name=name,
        secret_settings=secret_settings
    )

    # verification
    verifier.automation_runs.created()


def test_stop_run(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()
    given.automation_runs.exists(id=id)
    given.automation_runs.can_be_stopped(id=id)

    # action
    automation_run = api.automation_runs.get(id=id)
    automation_run.stop()

    # verification
    verifier.automation_runs.stopped(id=id)


def test_get_run_log(api, given):
    # precondition
    api.aa = True
    id = generator.uuid4()

    given.automation_runs.exists(id=id)

    # action
    automation_run = api.automation_runs.get(id=id)
    log_file = automation_run.get_log_file()

    # verification
    assert log_file


def test_get_run_state(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()
    expected_state = given.automation_runs.default_state()

    given.automation_runs.exists(id=id)
    given.automation_runs.has_state(id=id, state=expected_state)

    # action
    automation_run = api.automation_runs.get(id=id)
    state = automation_run.get_state()

    # verification
    assert expected_state == state
    verifier.automation_runs.state_fetched(id=id)


def test_rerun(api, given, verifier):
    # precondition
    api.aa = True

    inputs = {}
    name = generator.name()
    id = generator.uuid4()
    secret_settings = {generator.name(): generator.name()}

    given.automation_runs.has_rerun(
        id=id,
        secret_settings=secret_settings,
        inputs=inputs,
        name=name,
        merge=True
    )

    # action
    api.automation_runs.rerun(
        id=id, inputs=inputs, secret_settings=secret_settings, name=name,
        merge=True
    )

    # verification
    verifier.automation_runs.reran(id=id)


def test_update(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()
    new_name = generator.name()
    given.automation_runs.exists(id=id)
    run = api.automation_runs.get(id=id)

    # action
    run.name = new_name

    # verification
    verifier.automation_runs.updated(id=id)
