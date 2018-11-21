import faker
import pytest

generator = faker.Factory.create()


def test_exports_query(api, given, verifier):
    # preconditions
    total = 10
    given.exports.query(total=10)

    # action
    exports = api.exports.query(limit=10)

    # verification
    assert exports.total == total
    assert len(exports) == total

    verifier.exports.queried()


def test_exports_submit(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    file = generator.name()
    volume = generator.name()
    location = generator.name() + "/" + generator.name()
    given.exports.can_be_submitted(id=id)

    # action
    exports = api.exports.submit_export(file, volume, location)

    assert exports.id == id
    verifier.exports.submitted()


def test_exports_bulk_get(api, given, verifier):
    # preconditions
    total = 10

    export_ids = [generator.uuid4() for _ in range(total)]
    exports = [{'id': id_} for id_ in export_ids]
    given.exports.can_be_retrieved_in_bulk(exports)

    # action
    response = api.exports.bulk_get(export_ids)

    # verification
    assert len(response) == total
    verifier.exports.bulk_retrieved()


@pytest.mark.parametrize('copy_only', [True, False])
def test_exports_bulk_submit(api, given, verifier, copy_only):
    # preconditions
    total = 10

    exports = [
        {
            'file': generator.name(),
            'volume': generator.name(),
            'location': generator.name(),
            'properties': {},
            'overwrite': True
        }
        for _ in range(total)
    ]
    given.exports.can_be_submitted_in_bulk(exports)

    # action
    response = api.exports.bulk_submit(exports, copy_only=copy_only)

    # verification
    assert len(response) == total
    verifier.exports.bulk_submitted(copy_only)
