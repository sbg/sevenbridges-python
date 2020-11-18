import faker
import pytest

from sevenbridges.errors import NonJSONResponseError

generator = faker.Factory.create()


def test_non_json_response(api, given):
    # preconditions
    given.app.app_exist_non_json()

    # action
    with pytest.raises(NonJSONResponseError):
        api.apps.query(visibility="private")
