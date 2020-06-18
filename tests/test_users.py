# Users
def test_get_my_info(api, given, verifier):
    # preconditions
    given.user.authenticated()

    # action
    api.users.me()

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
