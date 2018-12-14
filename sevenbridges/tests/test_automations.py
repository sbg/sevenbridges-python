import faker
import pytest

generator = faker.Factory.create()
pytestmark = pytest.mark.automations


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
    verifier.automations.runs_retrieved(id)


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
