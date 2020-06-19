# noinspection PyProtectedMember
class Assert(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker

    def check_url(self, url):
        for hist in self.request_mocker._adapter.request_history:
            if hist.path == url:
                return True
        assert False, 'Path not matched {} != \n{}'.format(url, hist.path)

    def check_query(self, qs):
        for hist in self.request_mocker._adapter.request_history:
            if qs == hist.qs:
                return True
        assert False, 'Query string not matched \n{} != \n{}'.format(
            qs, hist.qs
        )

    def check_header_present(self, header):
        for hist in self.request_mocker._adapter.request_history:
            if header in hist.headers:
                return True
        assert False, 'AA headers missing'

    def check_post_data(self):
        for hist in self.request_mocker._adapter.request_history:
            print(hist)


class ProjectVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url('/projects/{}'.format(id))

    def queried(self, offset, limit):
        qs = {'offset': ['{}'.format(offset)], 'limit': ['{}'.format(limit)],
              'fields': ['_all']}
        self.checker.check_url('/projects/') and self.checker.check_query(qs)

    def created(self):
        self.checker.check_url('/projects')

    def query(self, name=None):
        qs = {'fields': ['_all']}
        if name:
            qs.update({'name': [name]})
        self.checker.check_url('/projects/') and self.checker.check_query(qs)

    def query_owner(self, owner, name=None):
        qs = {'fields': ['_all']}
        if name:
            qs.update({'name': [name]})
        self.checker.check_url(
            '/projects/{}'.format(owner)
        ) and self.checker.check_query(qs)

    def saved(self, id):
        self.checker.check_url('/projects/{}'.format(id))

    def member_retrieved(self, id, member_username):
        self.checker.check_url(
            '/projects/{}/members/{}'.format(id, member_username)
        )


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
        qs = {'project': [project], 'fields': ['_all']}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried(self, project):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10']}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_token(self, project):
        qs = {'project': [project],
              'fields': ['_all'],
              'limit': ['10'],
              'token': ['init']
              }
        self.checker.check_url(
            '/files/scroll'
        ) and self.checker.check_query(qs)

    def queried_with_parent(self, parent):
        qs = {'parent': [parent], 'fields': ['_all'], 'limit': ['10']}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_name(self, project, name):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10'],
              'name': [name]}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_metadata(self, project, key, value):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10'],
              'metadata.{}'.format(key): [value]}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_origin(self, project, key, value):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10'],
              'origin.{}'.format(key): [value]}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_tags(self, project, tags):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10'],
              'tag': tags}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def file_copied(self, id):
        self.checker.check_url('/files/{}/actions/copy'.format(id))

    def file_saved(self, id):
        self.checker.check_url(
            '/files/{}'.format(id)) and self.checker.check_url(
            '/files/{}/metadata'.format(id)
        )

    def file_saved_tags(self, id):
        self.checker.check_url(
            '/files/{}'.format(id)) and self.checker.check_url(
            '/files/{}/tags'.format(id)
        )

    def download_info_fetched(self, id):
        self.checker.check_url('/files/{}/download_info'.format(id))

    def bulk_retrieved(self):
        self.checker.check_url('/bulk/files/get')

    def bulk_updated(self):
        self.checker.check_url('/bulk/files/update')

    def bulk_edited(self):
        self.checker.check_url('/bulk/files/edit')

    def bulk_deleted(self):
        self.checker.check_url('/bulk/files/delete')

    def folder_created(self):
        self.checker.check_url('/files')

    def folder_files_listed(self, id):
        self.checker.check_url('/files/{}/list'.format(id))

    def folder_files_listed_scroll(self, id):
        qs = {'token': ['init'],
              'fields': ['_all']
              }
        self.checker.check_url(
            '/files/{}/scroll'.format(id)
        ) and self.checker.check_query(qs)

    def copied_to_folder(self, id):
        self.checker.check_url('/files/{}/actions/copy'.format(id))

    def moved_to_folder(self, id):
        self.checker.check_url('/files/{}/actions/move'.format(id))


class AppVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def apps_for_project_fetched(self, project):
        qs = {'project': [project]}
        self.checker.check_url('/apps') and self.checker.check_query(qs)

    def apps_fetched(self, visibility):
        if visibility:
            qs = {'visibility': [visibility]}
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
        qs = {'project': [project], 'fields': ['_all']}
        self.checker.check_url('/tasks') and self.checker.check_query(qs)

    def tasks_with_dates_fetched(self, project, testdate):
        qs = {
            'project': [project],
            'created_from': [testdate],
            'created_to': [testdate],
            'started_from': [testdate],
            'started_to': [testdate],
            'ended_from': [testdate],
            'ended_to': [testdate],
            'fields': ['_all']
        }
        self.checker.check_url('/tasks') and self.checker.check_query(qs)

    def task_fetched(self, id):
        self.checker.check_url('/tasks/{}'.format(id))

    def task_children_fetched(self, id):
        qs = {'parent': [id], 'fields': ['_all']}
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

    def bulk_retrieved(self):
        self.checker.check_url('/bulk/tasks/get')


class VolumeVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/storage/volumes')

    def created(self):
        self.checker.check_url('/storage/volumes')

    def modified(self, id):
        self.checker.check_url('/storage/volumes/{}'.format(id))

    def member_retrieved(self, id, member_username):
        self.checker.check_url(
            '/storage/volumes/{}/members/{}'.format(id, member_username)
        )


class MarkerVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/genome/markers')

    def created(self):
        self.checker.check_url('/genome/markers')

    def modified(self, _id):
        self.checker.check_url('/genome/markers/{}'.format(_id))


class ActionVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def feedback_received(self):
        self.checker.check_url('/action/notifications/feedback')

    def bulk_copy_done(self):
        self.checker.check_url('/action/files/copy')


class DivisionVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def division_fetched(self, id):
        self.checker.check_url('/divisions/{}'.format(id))

    def divisions_fetched(self):
        self.checker.check_url('/divisions')

    def teams_fetched(self, id):
        self.checker.check_url("/teams?division={}".format(id))


class TeamVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def team_fetched(self, id):
        self.checker.check_url('/teams/{}'.format(id))

    def teams_fetched(self):
        self.checker.check_url('/teams')

    def created(self):
        self.checker.check_url('/teams')

    def modified(self, id):
        self.checker.check_url('/teams/{}'.format(id))

    def members_fetched(self, id):
        self.checker.check_url('/teams/{}/members'.format(id))


class ImportsVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/storage/imports')

    def submitted(self):
        self.checker.check_url("/storage/imports")

    def bulk_retrieved(self):
        self.checker.check_url('/bulk/storage/imports/get')

    def bulk_submitted(self):
        self.checker.check_url('/bulk/storage/imports/create')


class ExportsVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/storage/exports')

    def submitted(self):
        self.checker.check_url("/storage/exports")

    def bulk_retrieved(self):
        self.checker.check_url('/bulk/storage/exports/get')

    def bulk_submitted(self, copy_only=False):
        qs = {'copy_only': [str(copy_only)]}
        self.checker.check_url('/bulk/storage/exports/create')
        self.checker.check_query(qs)


class DatasetVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url('/datasets/{}'.format(id))

    def queried(self, visibility=None):
        qs = {
            'fields': ['_all']
        }

        if visibility:
            qs['visibility'] = visibility

        self.checker.check_url('/datasets') and self.checker.check_query(qs)

    def owned_by(self, username):
        qs = {
            'fields': ['_all']
        }

        self.checker.check_url(
            '/datasets/{}'.format(username)) and self.checker.check_query(qs)

    def saved(self, id):
        self.checker.check_url('/datasets/{}'.format(id))

    def members_retrieved(self, id):
        self.checker.check_url('/datasets/{}/members'.format(id))

    def member_retrieved(self, id, member_username):
        self.checker.check_url(
            '/datasets/{}/members/{}'.format(id, member_username)
        )

    def member_removed(self, id, member_username):
        self.checker.check_url(
            '/datasets/{}/members/{}'.format(id, member_username)
        )

    def member_added(self, id):
        self.checker.check_url('/datasets/{}/members'.format(id))


class AutomationVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url('/automation/automations/{}'.format(id))

    def queried(self, name=None, include_archived=False):
        qs = {}
        if name:
            qs['name'] = [name]

        qs['include_archived'] = [str(include_archived)]

        self.checker.check_url('/automation/automations')
        self.checker.check_query(qs)

    def created(self):
        self.checker.check_url('/automation/automations')

    def saved(self, id):
        self.checker.check_url('/automation/automations/{id}'.format(id=id))

    def action_archive_performed(self, id):
        self.checker.check_url(
            '/automation/automations/{}/actions/archive'.format(id)
        )

    def action_restore_performed(self, id):
        self.checker.check_url(
            '/automation/automations/{}/actions/restore'.format(id)
        )

    def members_retrieved(self, id):
        self.checker.check_url(
            '/automation/automations/{}/members'.format(id)
        )

    def member_retrieved(self, id, member_username):
        self.checker.check_url(
            '/automation/automations/{}/members/{}'.format(id, member_username)
        )

    def packages_retrieved(self, id):
        self.checker.check_url(
            '/automation/automations/{}/packages'.format(id)
        )

    def package_retrieved(self, package_id):
        self.checker.check_url(
            '/automation/packages/{}'.format(package_id)
        )

    def runs_retrieved(self):
        self.checker.check_url(
            '/automation/runs'
        )

    def member_added(self, id):
        self.checker.check_url('/automation/automations/{}/members'.format(id))

    def member_removed(self, id, username):
        self.checker.check_url(
            '/automation/automations/{}/members/{}'.format(id, username))


class AutomationMemberVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def saved(self, automation, username):
        self.checker.check_url('/automation/automations/{}/members/{}'.format(
            automation, username
        ))


class AutomationPackageVerifier(object):

    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def created(self, automation_id):
        self.checker.check_url(
            '/automation/automations/{}/packages'.format(automation_id)
        )

    def action_archive_performed(self, automation_id, package_id):
        self.checker.check_url(
            "/automation/automations/{}"
            "/packages/{}/actions/archive".format(
                automation_id, package_id
            )
        )

    def action_restore_performed(self, automation_id, package_id):
        self.checker.check_url(
            "/automation/automations/{}"
            "/packages/{}/actions/restore".format(
                automation_id, package_id
            )
        )

    def saved(self, id):
        self.checker.check_url('/automation/packages/{id}'.format(id=id))


class AutomationRunVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url('/automation/runs/{}'.format(id))

    def queried(self, name=None):
        qs = {}
        if name:
            qs['name'] = [name]
        self.checker.check_url('/automation/runs')
        self.checker.check_query(qs)

    def log_fetched(self, id):
        self.checker.check_url('/automation/runs/{}/log'.format(id))

    def state_fetched(self, id):
        self.checker.check_url('/automation/runs/{}/state'.format(id))

    def created(self):
        self.checker.check_url('/automation/runs')

    def reran(self, id):
        self.checker.check_url('/automation/runs/{}/actions/rerun'.format(id))

    def stopped(self, id):
        self.checker.check_url('/automation/runs/{}/actions/stop'.format(id))

    def updated(self, id):
        self.checker.check_url('/automation/runs/{}'.format(id))


class AsyncJobVerifier(object):
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def listed(self, limit=None, offset=None):
        qs = {}
        if limit:
            qs['limit'] = limit
        if offset:
            qs['offset'] = offset
        self.checker.check_url('/async/files')
        self.checker.check_query(qs)

    def file_copy_job_fetched(self, id):
        self.checker.check_url('/async/files/copy/{}'.format(id))

    def file_delete_job_fetched(self, id):
        self.checker.check_url('/async/files/delete/{}'.format(id))

    def async_files_copied(self):
        self.checker.check_url('/async/files/copy')

    def async_files_deleted(self):
        self.checker.check_url('/async/files/delete')

    def file_move_job_fetched(self, id):
        self.checker.check_url('/async/files/move/{}'.format(id))

    def async_files_moved(self):
        self.checker.check_url('/async/files/move')
