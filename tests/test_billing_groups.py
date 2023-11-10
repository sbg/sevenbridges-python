import faker

generator = faker.Factory.create()


def test_billing_group_query(api, given, verifier):
    # preconditions
    total = 10
    given.billing_group.exist(total)

    # action
    billing_groups = api.billing_groups.query()

    # verification
    assert billing_groups.total == total
    assert len(billing_groups) == total

    verifier.billing_group.groups_fetched()
