import faker
import pytest

from sevenbridges.errors import NonJSONResponseError

generator = faker.Factory.create()


@pytest.mark.parametrize("status_code", [200, 500])
def test_non_json_response(api, given, status_code):
    # preconditions
    given.app.app_exist_non_json(status_code=status_code)

    # action
    with pytest.raises(NonJSONResponseError):
        api.apps.query(visibility="private")
