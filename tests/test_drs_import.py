import faker

generator = faker.Factory.create()


def test_imports_bulk_get(api, given, verifier):
    # preconditions
    total = 10
    file_ids = [generator.uuid4() for _ in range(total)]
    _import = {
        'id': generator.uuid4(),
        'result': [
            {'resource': {'id': _id, 'href': generator.url()}}
            for _id in file_ids
        ]
    }

    given.drs_imports.can_be_retrieved_in_bulk(_import)

    # action
    response = api.drs_imports.bulk_get(_import['id'])

    # verification
    assert len(response.result) == total
    verifier.drs_imports.bulk_retrieved(response.id)


def test_imports_bulk_submit(api, given, verifier):
    # preconditions
    total = 10

    imports = [
        {
            "drs_uri": generator.name(),
            "project": generator.name(),
            "metadata": {
                "study_id": generator.name(),
                "cohort": generator.name()
            },
            "name": generator.name()
        }
        for _ in range(total)
    ]
    tags = [generator.name()]

    given.drs_imports.can_be_submitted_in_bulk(imports)

    # action
    response = api.drs_imports.bulk_submit(imports, tags)

    # verification
    assert len(response.result) == total
    verifier.drs_imports.bulk_submitted()
