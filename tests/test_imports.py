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
    imports = api.imports.submit_import(
        volume=volume,
        location=location,
        project=project
    )

    assert imports.id == id
    verifier.imports.submitted()


def test_import_to_folder_submit(api, given, verifier):
    # preconditions
    id = generator.uuid4()
    volume = generator.name()
    location = generator.name()
    parent = generator.name() + "/"
    given.imports.can_be_submitted(id=id)
    preserve_folder_structure = False

    # action
    imports = api.imports.submit_import(
        volume=volume,
        location=location,
        parent=parent,
        preserve_folder_structure=preserve_folder_structure
    )

    assert imports.id == id
    verifier.imports.submitted()


def test_imports_bulk_get(api, given, verifier):
    # preconditions
    total = 10

    import_ids = [generator.uuid4() for _ in range(total)]
    imports = [{'id': id_} for id_ in import_ids]
    given.imports.can_be_retrieved_in_bulk(imports)

    # action
    response = api.imports.bulk_get(import_ids)

    # verification
    assert len(response) == total
    verifier.imports.bulk_retrieved()


def test_imports_bulk_submit(api, given, verifier):
    # preconditions
    total = 10

    imports = [
        {
            'volume': generator.name(),
            'location': generator.name(),
            'project': generator.name(),
            'name': generator.name(),
            'overwrite': True
        }
        for _ in range(total)
    ]
    given.imports.can_be_submitted_in_bulk(imports)

    # action
    response = api.imports.bulk_submit(imports)

    # verification
    assert len(response) == total
    verifier.imports.bulk_submitted()
