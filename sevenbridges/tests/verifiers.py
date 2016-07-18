from six.moves import urllib


# noinspection PyProtectedMember
class Assert(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker

    def check_url(self, url):
        for hist in self.request_mocker._adapter.request_history:
            if hist.path == url:
                return
        assert False, 'Path not matched!.'

    def check_query(self, query):
        for hist in self.request_mocker._adapter.request_history:
            if urllib.parse.urlencode(query) in hist.query:
                return
        assert False, 'Query string not matched!'


class ProjectVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url('/projects/{}'.format(id))

    def queried(self, offset, limit):
        qs = {'offset': offset, 'limit': limit}
        self.checker.check_url('/projects') and self.checker.check_query(qs)

    def created(self):
        self.checker.check_url('/projects')

    def saved(self, id):
        self.checker.check_url('/projects/{}'.format(id))


class MemberVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def members_fetched(self, project):
        self.checker.check_url('/projects/{}/members'.format(project))

    def member_added(self, project):
        self.checker.check_url('/projects/{}'.format(project))

    def member_removed(self, project, username):
        self.checker.check_url(
            '/projects/{}/members/{}'.format(project, username))

    def member_permissions_modified(self, project, username):
        self.checker.check_url('/projects/{}/members/{}/permissions'.format(
            project, username)
        )


class UserVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, username):
        self.checker.check_url('/users/{}'.format(username))

    def authenticated_user_fetched(self):
        self.checker.check_url('/user')


class EndpointVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self):
        self.checker.check_url('/')


class FileVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def files_for_project_fetched(self, project):
        qs = {'project': project}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried(self, project):
        qs = {'project': project}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_name(self, project, name):
        qs = {'project': project, 'name': name}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_metadata(self, project, key, value):
        qs = {'project': project, 'metadata.{}'.format(key): value}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_origin(self, project, key, value):
        qs = {'project': project, 'origin.{}'.format(key): value}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def file_copied(self, id):
        self.checker.check_url('/files/{}/actions/copy'.format(id))

    def file_saved(self, id):
        self.checker.check_url(
            '/files/{}'.format(id)) and self.checker.check_url(
            '/files/{}/metadata'.format(id)
        )

    def download_info_fetched(self, id):
        self.checker.check_url('/files/{}/download_info'.format(id))


class AppVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def apps_for_project_fetched(self, project):
        qs = {'project': project}
        self.checker.check_url('/apps') and self.checker.check_query(qs)

    def apps_fetched(self, visibility):
        if visibility:
            qs = {'visibility': visibility}
            self.checker.check_query(qs)
        self.checker.check_url('/apps')

    def app_fetched(self, id, revision):
        url = '/apps/{}/{}'.format(id, revision)
        self.checker.check_url(url)

    def app_copied(self, id):
        url = '/apps/{}/actions/copy'.format(id)
        self.checker.check_url(url)

    def app_installed(self, id):
        url = '/apps/{}/raw'.format(id)
        self.checker.check_url(url)

    def revision_created(self, id, revision):
        url = '/apps/{}/{}/raw'.format(id, revision)
        self.checker.check_url(url)


class TaskVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def tasks_for_project_fetched(self, project):
        qs = {'project': project}
        self.checker.check_url('/tasks') and self.checker.check_query(qs)

    def task_fetched(self, id):
        self.checker.check_url('/tasks/{}'.format(id))

    def task_children_fetched(self, id):
        qs = {'parent': id}
        self.checker.check_url(
            '/tasks/{}'.format(id)) and self.checker.check_query(qs)

    def task_created(self):
        self.checker.check_url('/tasks')

    def task_saved(self, id):
        self.checker.check_url('/tasks/{id}'.format(id=id))

    def action_performed(self, id, action):
        self.checker.check_url('/tasks/{}/actions/{}'.format(id, action))

    def execution_details_fetched(self, id):
        self.checker.check_url('/tasks/{id}/execution_details'.format(id=id))


class VolumeVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/storage/volumes')

    def created(self):
        self.checker.check_url('/storage/volumes')

    def modified(self, _id):
        self.checker.check_url('/storage/volumes/{}'.format(_id))
