import faker
import pytest

generator = faker.Factory.create()


@pytest.mark.parametrize("visibility", ["private", "public", None])
def test_apps_query(api, given, verifier, visibility):
    # preconditions
    total = 10
    given.app.apps_exist(visibility, total)

    # action
    apps = api.apps.query(visibility=visibility)

    # verification
    assert apps.total == total
    assert len(apps) == total

    verifier.app.apps_fetched(visibility)


def test_apps_get_revision(api, given, verifier):
    # preconditions
    app_id = 'me/my-project/my-app'
    app_revision = 1
    given.app.app_with_revision_exists(id=app_id, revision=app_revision)

    # action
    app = api.apps.get_revision(app_id, 1)

    # verification
    assert app.id == app_id
    assert app_id in repr(app)
    assert app.revision == app_revision

    verifier.app.app_fetched(app_id, app_revision)


@pytest.mark.parametrize("app_id", ['me/my-project', "me/my-project/1"])
def test_app_copy(api, given, verifier, app_id):
    # preconditions
    copied_name = 'new-app'
    app_revision = 1
    given.app.app_with_revision_exists(id=app_id, revision=app_revision)
    given.app.app_can_be_copied(id=app_id, new_name=copied_name)

    # action
    app = api.apps.get_revision(app_id, 1)
    app_copy = app.copy('me/my-project/', copied_name)

    # verification
    assert app_copy.name == copied_name

    verifier.app.app_copied(app_id)


def test_install_app(api, given, verifier):
    # preconditions
    app_id = "me/my-project/my-app"
    given.app.app_exists(id=app_id)
    given.app.app_can_be_installed(id=app_id)

    raw = {'sbg:id': app_id}

    # action
    app = api.apps.install_app(app_id, raw)

    # verification
    assert app.id == app_id
    verifier.app.app_installed(app_id)


def test_create_app_revision(api, given, verifier):
    # preconditions
    app_id = "me/my-project/my-app"
    revision = 1
    given.app.app_exists(id=app_id, revision=1)
    given.app.revision_can_be_created(id=app_id, revision=revision)

    raw = {'sbg:id': app_id, 'revision': revision}

    # action
    app_id_revision = '{}/{}'.format(app_id, str(revision))
    app = api.apps.create_revision(app_id_revision, revision, raw)

    # verification
    assert app.id == app_id
    assert app.revision == revision

    verifier.app.revision_created(app_id, revision)
