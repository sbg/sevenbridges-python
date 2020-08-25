import faker

generator = faker.Factory.create()


def test_get_division(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()
    given.division.exists(id=id)

    # action
    division = api.divisions.get(id=id)

    # verification
    assert division.id == id
    verifier.division.division_fetched(id=id)


def test_division_query(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    given.division.query(total)

    # action
    divisions = api.divisions.query()

    # verification
    assert len(divisions) == total

    verifier.division.divisions_fetched()


def test_get_teams(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    id = generator.uuid4()

    given.division.exists(id=id)
    given.division.teams_exist(id, total)

    division = api.divisions.get(id=id)
    teams = division.get_teams()

    assert len(teams) == total


def test_get_members(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    id = generator.uuid4()

    given.division.exists(id=id)
    given.division.members_exist(id, total)

    division = api.divisions.get(id=id)
    members = division.get_members()

    assert len(members) == total
