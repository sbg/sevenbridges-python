import faker

generator = faker.Factory.create()


def test_get_team(api, given, verifier):
    # precondition
    api.aa = True
    id = generator.uuid4()
    given.team.exists(id=id)

    # action
    team = api.teams.get(id=id)

    # verification
    assert team.id == id
    verifier.team.team_fetched(id=id)


def test_team_query(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    given.team.query(total)

    # action
    teams = api.teams.query(division=generator.name())

    # verification
    assert len(teams) == total
    verifier.team.teams_fetched()


def test_team_modify(api, given, verifier):
    api.aa = True

    id = generator.uuid4()
    new_name = generator.name()

    given.team.exists(id=id)
    given.team.modified(id=id, name=new_name)

    team = api.teams.get(id)
    team.name = new_name
    team.save()

    assert team.name == new_name
    verifier.team.modified(id=id)


def test_team_created(api, given, verifier):
    # preconditions
    api.aa = True
    name = generator.name()
    given.team.created(name)

    # action
    team = api.teams.create(name, division=generator.name())

    # verification
    assert team.name == name
    verifier.team.created()


def test_team_get_members(api, given, verifier):
    # preconditions
    api.aa = True
    total = 10
    id = generator.uuid4()

    given.team.exists(id=id)
    given.team_member.queried(id, total)

    # action
    team = api.teams.get(id)
    members = team.get_members()

    assert len(members) == total
    verifier.team.members_fetched(id)
