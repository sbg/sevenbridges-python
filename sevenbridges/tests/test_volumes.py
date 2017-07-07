import faker


generator = faker.Factory.create()


def test_volumes_query(api, given, verifier):
    # preconditions
    total = 10
    given.volume.can_be_queried(total)

    # action
    volumes = api.volumes.query()

    # verification
    assert volumes.total == total
    assert len(volumes) == total

    verifier.volume.queried()


def test_create_s3_volume(api, given, verifier):
    # preconditions
    name = generator.name()
    bucket = generator.name()
    access_key_id = generator.name()
    access_key_secret = generator.name()
    access_mode = 'RO'
    given.volume.volume_created(name='test')

    # action
    volume = api.volumes.create_s3_volume(name, bucket, access_key_id,
                                          access_key_secret, access_mode)

    # verifier
    assert volume.name == 'test'
    verifier.volume.created()


def test_create_google_volume(api, given, verifier):
    # preconditions
    name = generator.name()
    bucket = generator.name()
    access_key_id = generator.name()
    access_key_secret = generator.name()
    access_mode = 'RO'
    given.volume.volume_created(name='test')

    # action
    volume = api.volumes.create_google_volume(name, bucket, access_key_id,
                                              access_key_secret, access_mode)

    # verifier
    assert volume.name == 'test'
    verifier.volume.created()


def test_modify_volume(api, given, verifier):
    # preconditions
    _id = '{}/{}'.format('my', 'volume')
    name = generator.name()
    description = generator.name()
    given.volume.exist(id=_id, name=name, description=generator.name())
    given.volume.can_be_modified(id=_id, description=description)

    # action
    volume = api.volumes.get(_id)
    volume.description = description
    volume.save()

    # verifier
    assert volume.description == description
    verifier.volume.modified(volume.id)
