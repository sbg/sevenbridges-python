import faker

generator = faker.Factory.create()


def test_imports_query(api, given, verifier):
    # preconditions
    total = 10
    given.imports.query(total=10)

    # action
    imports = api.imports.query(limit=10)

    # verification
    assert imports.total == total
    assert len(imports) == total

    verifier.imports.queried()


def test_import_submit(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    volume = generator.name()
    location = generator.name()
    project = generator.name() + "/" + generator.name()
    given.imports.can_be_submitted(id=id)

    # action
    imports = api.imports.submit_import(volume, location, project)

    assert imports.id == id
    verifier.imports.submitted()
