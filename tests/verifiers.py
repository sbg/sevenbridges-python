# noinspection PyProtectedMember
class Assert:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker

    def check_url(self, url):
        for hist in self.request_mocker._adapter.request_history:
            if hist.path == url:
                return True
        assert False, f'Path not matched {url} != \n{hist.path}'

    def check_query(self, qs):
        for hist in self.request_mocker._adapter.request_history:
            if qs == hist.qs:
                return True
        assert False, f'Query string not matched \n{qs} != \n{hist.qs}'

    def check_header_present(self, header):
        for hist in self.request_mocker._adapter.request_history:
            if header in hist.headers:
                return True
        assert False, 'AA headers missing'

    def check_post_data(self):
        for hist in self.request_mocker._adapter.request_history:
            print(hist)


class ProjectVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url(f'/projects/{id}')

    def queried(self, offset, limit):
        qs = {
            'offset': [str(offset)],
            'limit': [str(limit)],
            'fields': ['_all']
        }
        self.checker.check_url('/projects/') and self.checker.check_query(qs)

    def created(self):
        self.checker.check_url('/projects')

    def query(self, name=None, category=None):
        qs = {'fields': ['_all']}
        if name:
            qs.update({'name': [name]})
        if category:
            qs.update({'category': [category]})
        self.checker.check_url('/projects/') and self.checker.check_query(qs)

    def query_owner(self, owner, name=None):
        qs = {'fields': ['_all']}
        if name:
            qs.update({'name': [name]})
        self.checker.check_url(
            f'/projects/{owner}'
        ) and self.checker.check_query(qs)

    def saved(self, id):
        self.checker.check_url(f'/projects/{id}')

    def member_retrieved(self, id, member_username):
        self.checker.check_url(f'/projects/{id}/members/{member_username}')


class MemberVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def members_fetched(self, project):
        self.checker.check_url(f'/projects/{project}/members')

    def member_added(self, project):
        self.checker.check_url(f'/projects/{project}')

    def member_removed(self, project, username):
        self.checker.check_url(f'/projects/{project}/members/{username}')

    def member_permissions_modified(self, project, username):
        self.checker.check_url(
            f'/projects/{project}/members/{username}/permissions'
        )


class UserVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, username):
        self.checker.check_url(f'/users/{username}')

    def authenticated_user_fetched(self):
        self.checker.check_url('/user')


class EndpointVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self):
        self.checker.check_url('/')


class FileVerifier:
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
              f'metadata.{key}': [value]}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_origin(self, project, key, value):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10'],
              f'origin.{key}': [value]}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def queried_with_file_tags(self, project, tags):
        qs = {'project': [project], 'fields': ['_all'], 'limit': ['10'],
              'tag': tags}
        self.checker.check_url('/files') and self.checker.check_query(qs)

    def file_copied(self, id):
        self.checker.check_url(f'/files/{id}/actions/copy')

    def file_saved(self, id):
        self.checker.check_url(f'/files/{id}')
        self.checker.check_url(f'/files/{id}/metadata')

    def file_saved_tags(self, id):
        self.checker.check_url(f'/files/{id}')
        self.checker.check_url(f'/files/{id}/tags')

    def download_info_fetched(self, id):
        self.checker.check_url(f'/files/{id}/download_info')

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
        self.checker.check_url(f'/files/{id}/list')

    def folder_files_listed_scroll(self, id):
        qs = {'token': ['init'], 'fields': ['_all']}
        self.checker.check_url(f'/files/{id}/scroll')
        self.checker.check_query(qs)

    def copied_to_folder(self, id):
        self.checker.check_url(f'/files/{id}/actions/copy')

    def moved_to_folder(self, id):
        self.checker.check_url(f'/files/{id}/actions/move')


class AppVerifier:
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
        url = f'/apps/{id}/{revision}'
        self.checker.check_url(url)

    def app_copied(self, id):
        url = f'/apps/{id}/actions/copy'
        self.checker.check_url(url)

    def app_installed(self, id):
        url = f'/apps/{id}/raw'
        self.checker.check_url(url)

    def revision_created(self, id, revision):
        url = f'/apps/{id}/{revision}/raw'
        self.checker.check_url(url)


class TaskVerifier:
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
        self.checker.check_url('/tasks')
        self.checker.check_query(qs)

    def task_fetched(self, id):
        self.checker.check_url(f'/tasks/{id}')

    def task_children_fetched(self, id):
        qs = {'parent': [id], 'fields': ['_all']}
        self.checker.check_url(f'/tasks/{id}')
        self.checker.check_query(qs)

    def task_created(self):
        self.checker.check_url('/tasks')

    def task_saved(self, id):
        self.checker.check_url(f'/tasks/{id}')

    def action_performed(self, id, action):
        self.checker.check_url(f'/tasks/{id}/actions/{action}')

    def execution_details_fetched(self, id):
        self.checker.check_url(f'/tasks/{id}/execution_details')

    def bulk_retrieved(self):
        self.checker.check_url('/bulk/tasks/get')


class VolumeVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/storage/volumes')

    def created(self):
        self.checker.check_url('/storage/volumes')

    def modified(self, id):
        self.checker.check_url(f'/storage/volumes/{id}')

    def member_retrieved(self, id, member_username):
        self.checker.check_url(
            f'/storage/volumes/{id}/members/{member_username}'
        )


class MarkerVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def queried(self):
        self.checker.check_url('/genome/markers')

    def created(self):
        self.checker.check_url('/genome/markers')

    def modified(self, _id):
        self.checker.check_url(f'/genome/markers/{_id}')


class ActionVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def feedback_received(self):
        self.checker.check_url('/action/notifications/feedback')

    def bulk_copy_done(self):
        self.checker.check_url('/action/files/copy')


class DivisionVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def division_fetched(self, id):
        self.checker.check_url(f'/divisions/{id}')

    def divisions_fetched(self):
        self.checker.check_url('/divisions')

    def teams_fetched(self, id):
        self.checker.check_url(f'/teams?division={id}')


class TeamVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def team_fetched(self, id):
        self.checker.check_url(f'/teams/{id}')

    def teams_fetched(self):
        self.checker.check_url('/teams')

    def created(self):
        self.checker.check_url('/teams')

    def modified(self, id):
        self.checker.check_url(f'/teams/{id}')

    def members_fetched(self, id):
        self.checker.check_url(f'/teams/{id}/members')


class ImportsVerifier:
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


class ExportsVerifier:
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


class DatasetVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url(f'/datasets/{id}')

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

        self.checker.check_url(f'/datasets/{username}')
        self.checker.check_query(qs)

    def saved(self, id):
        self.checker.check_url(f'/datasets/{id}')

    def members_retrieved(self, id):
        self.checker.check_url(f'/datasets/{id}/members')

    def member_retrieved(self, id, member_username):
        self.checker.check_url(f'/datasets/{id}/members/{member_username}')

    def member_removed(self, id, member_username):
        self.checker.check_url(f'/datasets/{id}/members/{member_username}')

    def member_added(self, id):
        self.checker.check_url(f'/datasets/{id}/members')


class AutomationVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url(f'/automation/automations/{id}')

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
        self.checker.check_url(f'/automation/automations/{id}')

    def action_archive_performed(self, id):
        self.checker.check_url(f'/automation/automations/{id}/actions/archive')

    def action_restore_performed(self, id):
        self.checker.check_url(f'/automation/automations/{id}/actions/restore')

    def members_retrieved(self, id):
        self.checker.check_url(f'/automation/automations/{id}/members')

    def member_retrieved(self, id, member_username):
        self.checker.check_url(
            f'/automation/automations/{id}/members/{member_username}'
        )

    def packages_retrieved(self, id):
        self.checker.check_url(f'/automation/automations/{id}/packages')

    def package_retrieved(self, package_id):
        self.checker.check_url(f'/automation/packages/{package_id}')

    def runs_retrieved(self):
        self.checker.check_url('/automation/runs')

    def member_added(self, id):
        self.checker.check_url(f'/automation/automations/{id}/members')

    def member_removed(self, id, username):
        self.checker.check_url(
            f'/automation/automations/{id}/members/{username}'
        )


class AutomationMemberVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def saved(self, automation, username):
        self.checker.check_url(
            f'/automation/automations/{automation}/members/{username}'
        )


class AutomationPackageVerifier:

    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def created(self, automation_id):
        self.checker.check_url(
            f'/automation/automations/{automation_id}/packages'
        )

    def action_archive_performed(self, automation_id, package_id):
        self.checker.check_url(
            f'/automation/automations/{automation_id}'
            f'/packages/{package_id}/actions/archive'
        )

    def action_restore_performed(self, automation_id, package_id):
        self.checker.check_url(
            f'/automation/automations/{automation_id}'
            f'/packages/{package_id}/actions/restore'
        )

    def saved(self, id):
        self.checker.check_url(f'/automation/packages/{id}')


class AutomationRunVerifier:
    def __init__(self, request_mocker):
        self.request_mocker = request_mocker
        self.checker = Assert(self.request_mocker)

    def fetched(self, id):
        self.checker.check_url(f'/automation/runs/{id}')

    def queried(self, name=None):
        qs = {}
        if name:
            qs['name'] = [name]
        self.checker.check_url('/automation/runs')
        self.checker.check_query(qs)

    def log_fetched(self, id):
        self.checker.check_url(f'/automation/runs/{id}/log')

    def state_fetched(self, id):
        self.checker.check_url(f'/automation/runs/{id}/state')

    def created(self):
        self.checker.check_url('/automation/runs')

    def reran(self, id):
        self.checker.check_url(f'/automation/runs/{id}/actions/rerun')

    def stopped(self, id):
        self.checker.check_url(f'/automation/runs/{id}/actions/stop')

    def updated(self, id):
        self.checker.check_url(f'/automation/runs/{id}')


class AsyncJobVerifier:
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
        self.checker.check_url(f'/async/files/copy/{id}')

    def file_delete_job_fetched(self, id):
        self.checker.check_url(f'/async/files/delete/{id}')

    def async_files_copied(self):
        self.checker.check_url('/async/files/copy')

    def async_files_deleted(self):
        self.checker.check_url('/async/files/delete')

    def file_move_job_fetched(self, id):
        self.checker.check_url(f'/async/files/move/{id}')

    def async_files_moved(self):
        self.checker.check_url('/async/files/move')
