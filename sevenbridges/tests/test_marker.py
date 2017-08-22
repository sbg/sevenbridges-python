import faker

generator = faker.Factory.create()


def test_markers_query(api, given, verifier):
    # preconditions
    total = 10
    file = generator.name()
    given.marker.query(total=10, file=file)

    # action
    markers = api.markers.query(file=file)

    # verification
    assert markers.total == total
    assert len(markers) == total

    verifier.marker.queried()


def test_marker_create(api, given, verifier):
    # preconditions
    file = generator.uuid4()
    name = generator.name()
    chromosome = "chr1"
    position = {
        "start": 0,
        "end": 10
    }
    given.marker.created(name=name, file=file)

    marker = api.markers.create(file, name, position, chromosome)

    # verifier
    assert marker.name == name
    verifier.marker.created()


def test_modify_marker(api, given, verifier):
    # preconditions
    _id = '{}/{}'.format('my', 'marker')
    name = generator.name()
    given.marker.exists(id=_id)
    given.marker.modified(id=_id, name=name)

    # action
    marker = api.markers.get(_id)
    marker.name = name
    marker.save()

    # verifier
    assert marker.name == name
    verifier.marker.modified(marker.id)
