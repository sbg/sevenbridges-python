import faker

generator = faker.Factory.create()


# Endpoints
def test_endpoints(api, given, verifier):
    # preconditions
    given.endpoints.defined()

    # action
    endpoints = api.endpoints.get()

    # verification
    assert 'upload' in endpoints.upload_url
    assert 'projects' in endpoints.projects_url
    assert 'action' in endpoints.action_url
    assert 'user' in endpoints.user_url
    assert 'users' in endpoints.users_url
    assert 'tasks' in endpoints.tasks_url
    assert 'apps' in endpoints.apps_url
    verifier.endpoints.fetched()


# Users
def test_get_my_info(api, given, verifier):
    # preconditions
    given.user.authenticated()

    # action
    _ = api.users.me()

    # verification
    verifier.user.authenticated_user_fetched()


def test_get_users_info(api, given, verifier):
    # preconditions
    username = 'test'
    given.user.exists(username=username)

    # action
    user = api.users.get(username)

    # verification
    assert user.username == username
    assert username in repr(user)
    verifier.user.fetched(username)


def test_user_equality(api, given, verifier):
    # preconditions
    username = 'test'
    given.user.authenticated()
    given.user.exists(username=username)

    # action
    me = api.users.me()
    other = api.users.get(username)

    # verification
    assert me != other
    verifier.user.authenticated_user_fetched()
    verifier.user.fetched(username)
