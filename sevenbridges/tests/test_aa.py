import faker

from sevenbridges import Project
from sevenbridges.http.advance_access import advance_access

generator = faker.Factory.create()


def test_aa_ctx_manager(api, given, verifier):
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)
    given.project.exists(id=id)

    with advance_access(api):
        api.projects.get(id=id)

    verifier.aa.headers_present()


def test_aa_decorator(api, given, verifier):
    owner = generator.user_name()
    project_short_name = generator.slug()
    id = '{}/{}'.format(owner, project_short_name)

    Project.get_members = advance_access()(Project.get_members)
    given.project.exists(id=id)
    given.member.members_exist(project=id, num_of_members=2)

    project = api.projects.get(id=id)

    project.get_members()
    verifier.aa.headers_present()
