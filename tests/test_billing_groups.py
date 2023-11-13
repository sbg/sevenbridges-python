import pytest
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


@pytest.mark.parametrize('with_cost', [True, False])
def test_billing_storage_breakdown(api, given, verifier, with_cost):
    # precondition
    given.billing_group.exist(1)

    # action
    billing_groups = api.billing_groups.query()
    billing_group = billing_groups[0]

    # precondition
    total = 5
    given.billing_group_storage_breakdown.exist(
        bg_id=billing_group.id,
        num_of_objects=total,
        with_cost=with_cost
    )

    # action
    storage_breakdown = billing_group.storage_breakdown()

    # verification
    verifier.billing_group.groups_fetched()
    verifier.billing_group_storage_breakdown.fetched(
        billing_group=billing_group
    )

    verifier.billing_group_storage_breakdown.fetched(
        billing_group=billing_group
    )
    assert len(storage_breakdown) == total
    for breakdown in storage_breakdown:
        if with_cost:
            assert breakdown.active is not None
            assert breakdown.archived is not None
        else:
            assert breakdown.active is None
            assert breakdown.archived is None
