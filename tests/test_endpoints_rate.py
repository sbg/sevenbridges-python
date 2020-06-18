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


# Rate
def test_rate_limit(api, given):
    # preconditions
    mock = {'rate': {'limit': 100, 'remaining': 20},
            'instance_limit': {'limit': 100, 'remaining': 20}}
    given.rate.limit_available(**mock)

    # action
    result = api.rate_limit.get()

    assert result.rate.limit == mock['rate']['limit']
    assert result.rate.remaining == mock['rate']['remaining']
    assert result.instance_limit.limit == mock['instance_limit']['limit']
    assert result.instance_limit.remaining == mock['instance_limit'][
        'remaining']
