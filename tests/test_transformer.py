import uuid
from datetime import datetime

import faker
import pytest

from sevenbridges import (
    Project, Task, App, File,
    User, BillingGroup, Marker, Division
)
from sevenbridges.errors import SbgError
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.team import Team
from sevenbridges.models.volume import Volume

generator = faker.Factory.create()


def random_uuid():
    return str(uuid.uuid4())


@pytest.mark.parametrize("project", ['u/p', Project(id='u/p')])
def test_transform_project(project):
    Transform.to_project(project)


@pytest.mark.parametrize("project", [[], {}, b'', None, type])
def test_transform_project_invalid_values(project):
    with pytest.raises(SbgError):
        Transform.to_project(project)


@pytest.mark.parametrize("task", [random_uuid(), Task(id=random_uuid())])
def test_transform_task(task):
    Transform.to_task(task)


@pytest.mark.parametrize("task", [[], {}, b'', None, type])
def test_transform_task_invalid_values(task):
    with pytest.raises(SbgError):
        Transform.to_task(task)


@pytest.mark.parametrize("app", ['u/p/a/0', App(id='u/p/a/1')])
def test_transform_app(app):
    Transform.to_app(app)


@pytest.mark.parametrize("app", [[], {}, b'', None, type])
def test_transform_app_invalid_values(app):
    with pytest.raises(SbgError):
        Transform.to_task(app)


@pytest.mark.parametrize("file", [random_uuid(), File(id=random_uuid())])
def test_transform_file(file):
    Transform.to_file(file)


@pytest.mark.parametrize("file", [[], {}, b'', None, type])
def test_transform_file_invalid_values(file):
    with pytest.raises(SbgError):
        Transform.to_file(file)


@pytest.mark.parametrize("user", ['u', User(username='u')])
def test_transform_user(user):
    Transform.to_user(user)


@pytest.mark.parametrize("user", [[], {}, b'', None, type])
def test_transform_user_invalid_values(user):
    with pytest.raises(SbgError):
        Transform.to_user(user)


@pytest.mark.parametrize(
    "group", [random_uuid(), BillingGroup(id=random_uuid())]
)
def test_transform_billing_group(group):
    Transform.to_billing_group(group)


@pytest.mark.parametrize("group", [[], {}, b'', None, type])
def test_transform_billing_group_invalid_values(group):
    with pytest.raises(SbgError):
        Transform.to_billing_group(group)


@pytest.mark.parametrize("volume", ['u/p', Volume(id='u/p')])
def test_transform_volume(volume):
    Transform.to_volume(volume)


@pytest.mark.parametrize("volume", [[], {}, b'', None, type])
def test_transform_volume_invalid_values(volume):
    with pytest.raises(SbgError):
        Transform.to_volume(volume)


@pytest.mark.parametrize("datestring,expected", [
    ('2017-01-10T14:04:23', '2017-01-10T14:04:23'),
    (datetime(2017, 1, 10, 14, 4, 23, 838459), '2017-01-10T14:04:23'),
])
def test_transform_datestring(datestring, expected):
    assert Transform.to_datestring(datestring) == expected


@pytest.mark.parametrize("datestring", ['', None, [], {}])
def test_transform_datestring_invalid(datestring):
    with pytest.raises(SbgError):
        Transform.to_datestring(datestring)


@pytest.mark.parametrize("marker", [str(generator.uuid4()),
                                    Marker(id=generator.uuid4())])
def test_transform_marker(marker):
    Transform.to_marker(marker)


@pytest.mark.parametrize("division", [generator.name(),
                                      Division(id=generator.name())])
def test_transform_divisions(division):
    Transform.to_division(division)


@pytest.mark.parametrize("team", [str(generator.uuid4()),
                                  Team(id=generator.uuid4())])
def test_transform_teams(team):
    Transform.to_team(team)
