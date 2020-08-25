import faker

generator = faker.Factory.create()


def test_get(api, given, verifier):
    # precondition
    api.aa = True
    username = generator.user_name()
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)

    # action
    dataset = api.datasets.get(id=id)

    # verification
    assert dataset.id == id
    verifier.datasets.fetched(id=id)


def test_query(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    given.datasets.query(total)

    # action
    datasets = api.datasets.query()

    # verification
    assert len(datasets) == total

    verifier.datasets.queried()


def test_query_by_owner(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    username = generator.user_name()
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)
    given.datasets.owned_by(total, username)

    # action
    datasets = api.datasets.get_owned_by(username)

    # verification
    assert len(datasets) == total

    verifier.datasets.owned_by(username)


def test_save(api, given, verifier):
    # precondition
    api.aa = True
    username = generator.user_name()
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)
    given.datasets.can_be_saved(id=id)

    # action
    dataset = api.datasets.get(id=id)
    dataset.name = generator.slug()
    dataset.description = generator.slug()
    dataset.save()

    # verification
    verifier.datasets.saved(id)


def test_get_members(api, given, verifier):
    # precondition
    api.aa = True
    total = 10
    username = generator.user_name()
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)
    given.datasets.has_members(id, dataset_name, total)

    # action
    dataset = api.datasets.get(id)
    members = dataset.get_members()

    # verification
    assert len(members) == total
    verifier.datasets.members_retrieved(id)


def test_get_member(api, given, verifier):
    # precondition
    api.aa = True
    username = generator.user_name()
    member_username = generator.user_name()
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)
    given.datasets.has_member(id, dataset_name, member_username)

    # action
    dataset = api.datasets.get(id)
    member = dataset.get_member(member_username)

    # verification
    assert member.username == member_username
    verifier.datasets.member_retrieved(id, member_username)


def test_add_member(api, given, verifier):
    # precondition
    api.aa = True
    username = generator.user_name()
    member_username = generator.user_name()
    member_permissions = {
        "write": True,
        "read": True,
        "copy": True,
        "execute": True,
        "admin": True
    }
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)
    given.datasets.can_add_member(id, member_username)

    # action
    dataset = api.datasets.get(id)
    dataset.add_member(member_username, member_permissions)

    # verification
    verifier.datasets.member_added(id)


def test_remove_member(api, given, verifier):
    # precondition
    api.aa = True
    username = generator.user_name()
    member_username = generator.user_name()
    dataset_name = generator.slug()
    id = '{}/{}'.format(username, dataset_name)
    given.datasets.exists(id=id)
    given.datasets.has_member(id, dataset_name, member_username)
    given.datasets.can_remove_member(id, member_username)

    # action
    dataset = api.datasets.get(id)
    dataset.remove_member(member_username)

    # verification
    verifier.datasets.member_removed(id, member_username)
