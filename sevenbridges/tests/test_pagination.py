import faker

generator = faker.Factory.create()


def test_single_page_pagination(api, given, verifier):
    # preconditions
    limit = 2
    total = 10
    given.project.paginated_projects(limit, total)
    # action
    projects = api.projects.query(offset=0, limit=limit)

    # verification
    assert projects.total == total
    assert len(projects) == limit
    verifier.project.queried(0, limit)


def test_all_pages_pagination(api, given, verifier):
    # preconditions
    limit = 2
    total = 10
    given.project.paginated_projects(limit, total)

    # action
    projects = api.projects.query(offset=0, limit=limit)

    # verification
    assert len(list(projects.all())) == total
    for i in range(0, limit, total):
        verifier.project.queried(i, limit)


def test_single_page_back(api, given, verifier):
    # preconditions
    limit = 2
    total = 10
    given.project.paginated_projects(limit, total)

    # action
    projects = api.projects.query(offset=4, limit=limit)

    # verification
    projects.previous_page()
    verifier.project.queried(2, limit)
