import faker

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
