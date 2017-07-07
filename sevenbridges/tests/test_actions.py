import faker

generator = faker.Factory.create()


def test_action_feedback(api, given, verifier):
    # given
    given.action.feedback_set()

    # send feedback
    api.actions.send_feedback(text=generator.name())

    # verify
    verifier.action.feedback_received()


def test_action_bulk_copy(api, given, verifier):

    file_id = generator.uuid4()
    # given
    given.action.can_bulk_copy(id=file_id)

    # copy files
    result = api.actions.bulk_copy_files([file_id], "test")

    # verify
    assert file_id in result.values()
    verifier.action.bulk_copy_done()
