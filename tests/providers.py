import re
import time

import faker

from sevenbridges.meta.resource import TOTAL_MATCH_HEADER

generator = faker.Factory.create()


class EndpointProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def endpoints(self):
        return {
            'rate_limit_url': f'{self.base_url}/v2/rate_limit',
            'user_url': f'{self.base_url}/v2/user',
            'users_url': f'{self.base_url}/v2/users',
            'billing_url': f'{self.base_url}/v2/billing',
            'projects_url': f'{self.base_url}/v2/projects',
            'files_url': f'{self.base_url}/v2/files',
            'tasks_url': f'{self.base_url}/v2/tasks',
            'apps_url': f'{self.base_url}/v2/apps',
            'action_url': f'{self.base_url}/v2/action',
            'upload_url': f'{self.base_url}/v2/upload'
        }

    def defined(self):
        self.request_mocker.get('/', json=self.endpoints())


class RateLimitProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_rate():
        return {
            'rate': {
                'limit': 1000,
                "remaining": 1000,
                'reset': (int(time.time() + 60))
            },
            'instance_limit': {
                'limit': 1000,
                'remaining': 999
            }
        }

    def limit_available(self, **kwargs):
        rate = self.default_rate()
        rate.update(kwargs)
        self.request_mocker.get('/rate_limit', json=rate)


class UserProvider:
    """
    Server side user data mocking.
    """

    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_user():
        return {
            'username': generator.user_name(),
            'email': generator.email(),
            'last_name': generator.last_name(),
            'first_name': generator.first_name(),
            'address': generator.address(),
            'city': generator.city(),
            'country': generator.country(),
            'state': generator.state()
        }

    def authenticated(self):
        user = self.default_user()
        self.request_mocker.get('/user', json=user)

    def exists(self, **kwargs):
        user = self.default_user()
        user.update(kwargs)
        username = user['username']
        self.request_mocker.get(f'/users/{username}', json=user)


class ProjectProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.member_provider = MemberProvider(request_mocker, base_url)

    @staticmethod
    def default_project():
        return {
            'href': generator.url(),
            'id': 'my/my-project',
            'name': generator.user_name(),
            'billing_group': generator.uuid4(),
            'category': generator.user_name(),
            'settings': {},
            'tags': []
        }

    def exists(self, **kwargs):
        project = self.default_project()
        project.update(kwargs)
        id = project['id']
        self.request_mocker.get(f'/projects/{id}', json=project)

    def query(self, total, **kwargs):
        items = [ProjectProvider.default_project() for _ in range(total)]
        items[0].update(**kwargs)
        name = kwargs.get('name')
        owner = kwargs.get('owner')
        url = '/projects/?fields=_all'
        if owner:
            url = f'/projects/{owner}?fields=_all'
        if name:
            url += f'&name={name}'
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response,
                                headers={TOTAL_MATCH_HEADER: str(total)})

    def can_be_created(self, **kwargs):
        project = self.default_project()
        [project.pop(key) for key in ['id', 'href']]
        project.update(**kwargs)
        self.request_mocker.request('POST', '/projects', json=project)

    def can_be_saved(self, **kwargs):
        project = self.default_project()
        project.update(**kwargs)
        id = project['id']
        self.request_mocker.patch(f'/projects/{id}', json=project)

    def paginated_projects(self, limit, num_of_projects):
        items = [ProjectProvider.default_project() for _ in
                 range(num_of_projects)]
        for i in range(0, num_of_projects, limit):
            href = f'{self.base_url}/projects/?offset={i}&limit={limit}'
            sub_items = items[i:i + limit]
            links = []
            if i + limit < num_of_projects:
                next_url = (
                    f'/projects/?offset={i + limit}&limit={limit}&fields=_all'
                )
                next_page_link = {
                    'method': 'GET',
                    'rel': 'next',
                    'href': self.base_url + next_url
                }
                links.append(next_page_link)

            if i > limit:
                prev_url = (
                   f'/projects/?offset={i - limit}&limit={limit}&fields=_all'
                )
                prev = {
                    'method': 'GET',
                    'rel': 'prev',
                    'href': self.base_url + prev_url
                }
                links.append(prev)

            response = {
                'href': href,
                'items': sub_items,
                'links': links
            }
            self.request_mocker.get(
                href, json=response, headers={
                    TOTAL_MATCH_HEADER: str(num_of_projects)
                }
            )

    def has_member(self, id, project_name, member_username):
        member = self.member_provider.default_member(
            username=member_username,
            project=project_name
        )

        href = f'{self.base_url}/projects/{id}/members/{member_username}'
        self.request_mocker.get(href, json=member)


class MemberProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def default_member(self, project=None, username=None, dataset=None,
                       volume=None):
        if username is None:
            username = generator.user_name()

        if dataset is not None:
            url = f'{self.base_url}/datasets/{dataset}/members/{username}'
        elif volume is not None:
            url = f'{self.base_url}/storage/volumes{volume}/members/{username}'
        else:
            project = project or generator.name()
            url = f'{self.base_url}/projects/{project}/members/{username}'

        return {
            'href': url,
            'username': username,
            'permissions': {
                'write': True,
                'read': True,
                'execute': False,
                'admin': False,
                'copy': False
            }
        }

    def members_exist(self, project, num_of_members):
        items = [self.default_member(project, 'test') for _ in
                 range(num_of_members)]
        href = f'{self.base_url}/projects/{project}/members'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_members)})

    def member_exist(self, project, username=None, email=None):
        member = self.default_member(project, username)
        if username:
            member.update({'username': username})
        if email:
            member.update({'email': email})
        href = f'{self.base_url}/projects/{project}/members'
        self.request_mocker.request('POST', href, json=member)
        return member

    def can_be_removed(self, project, username):
        href = f'{self.base_url}/projects/{project}/members/{username}'
        self.request_mocker.delete(href, status_code=204)

    def permissions_can_be_modified(self, project, username):
        href = (
            f'{self.base_url}/projects/{project}'
            f'/members/{username}/permissions'
        )
        self.request_mocker.patch(href, status_code=200)


class FileProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_file():
        return {
            'href': generator.url(),
            'id': generator.uuid4(),
            'parent': generator.uuid4(),
            'name': generator.user_name(),
            'project': 'my/test-project',
            'metadata': {
                'sample': generator.name()
            },
            'tags': [
                generator.name()
            ],
            'type': generator.slug()
        }

    @staticmethod
    def download_info():
        return {
            'url': generator.url()
        }

    def exists(self, **kwargs):
        file_ = FileProvider.default_file()
        file_.update(kwargs)
        id_ = file_['id']
        href = f'{file_["href"]}files/{id_}'
        file_['href'] = href
        self.request_mocker.get(f'/files/{id_}', json=file_)

    def exist(self, files):
        all_files = []
        for file_data in files:
            file_ = FileProvider.default_file()
            file_.update(file_data)
            id_ = file_['id']
            href = f'{file_["href"]}files/{id_}'
            file_['href'] = href
            self.request_mocker.get(f'/files/{id_}', json=file_)
            all_files.append({'resource': file_})

        data = {'items': all_files}
        self.request_mocker.post('/bulk/files/get', json=data)

    def can_be_updated_in_bulk(self, files):
        all_files = []
        for file_data in files:
            file_ = FileProvider.default_file()
            file_.update(file_data)
            all_files.append({'resource': file_})
        data = {'items': all_files}
        self.request_mocker.post('/bulk/files/update', json=data)

    def can_be_edited_in_bulk(self, files):
        all_files = []
        for file_data in files:
            file_ = FileProvider.default_file()
            file_.update(file_data)
            all_files.append({'resource': file_})
        data = {'items': all_files}
        self.request_mocker.post('/bulk/files/edit', json=data)

    def can_be_deleted_in_bulk(self, files):
        all_files = []
        for file_data in files:
            file_ = FileProvider.default_file()
            file_.update(file_data)
            all_files.append({'resource': file_})
        data = {'items': all_files}
        self.request_mocker.post('/bulk/files/delete', json=data)

    def download_info_defined(self, id):
        json = self.download_info()
        url = f'/files/{id}/download_info'
        self.request_mocker.get(url, json=json)

    def can_be_copied(self, id=None, new_id=None):
        file_ = FileProvider.default_file()
        file_['id'] = new_id
        self.request_mocker.request(
            'POST', f'/files/{id}/actions/copy', json=file_)

    def can_be_saved(self, id=None):
        file_ = FileProvider.default_file()
        file_['id'] = id
        self.request_mocker.patch(f'/files/{id}', json=file_)

    def metadata_can_be_saved(self, id):
        file_ = FileProvider.default_file()
        self.request_mocker.patch(
            f'/files/{id}/metadata', json=file_['metadata']
        )

    def tags_can_be_saved(self, id):
        file_ = FileProvider.default_file()
        self.request_mocker.request(
            'PUT', f'/files/{id}/tags', json=file_['tags']
        )

    def files_exist_for_project(self, project, num_of_files, scroll=False):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        suffix = 'files/scroll' if scroll else 'files'
        href = f'{self.base_url}/{suffix}?project={project}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def files_exist_for_folder(self, folder_id, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        href = f'{self.base_url}/files?parent={folder_id}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def files_exist_for_file_name(self, project, file_name, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        href = f'{self.base_url}/files?project={project}&name={file_name}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def files_exist_for_file_metadata(self, project, key, value, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        href = (
            f'{self.base_url}/files?project={project}&metadata.{key}={value}'
        )
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def files_exist_for_file_origin(self, project, key, value, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        href = f'{self.base_url}/files?project={project}&origin.{key}={value}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def files_exist_for_file_tag(self, project, tags, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        href = (
            f'{self.base_url}/files?'
            f'project={project}&tag={tags[0]}&tag={tags[1]}'
        )
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def files_in_folder(self, num_of_files, folder_id, scroll=False):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        suffix = 'scroll' if scroll else 'list'
        href = f'{self.base_url}/files/{folder_id}/{suffix}'
        response = {
            'href': href,
            'items': items,
            'links': []
        }

        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_files)})

    def can_create_folder(self, id=None):
        file_ = self.default_file()
        file_['id'] = id
        file_['type'] = 'folder'
        self.request_mocker.post('/files', json=file_)

    def can_copy_to_folder(self, id=None, parent=None, name=None, new_id=None):
        file_ = self.default_file()
        file_['id'] = new_id
        file_['parent'] = parent
        if name:
            file_['name'] = name

        self.request_mocker.post(f'/files/{id}/actions/copy', json=file_)

    def can_move_to_folder(self, id=None, parent=None, name=None):
        file_ = self.default_file()
        file_['id'] = id
        result = {
            'parent': parent
        }
        if name:
            result['name'] = name

        self.request_mocker.post(f'/files/{id}/actions/move', json=result)


class AppProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_app():
        id = generator.uuid4()
        return {
            'href': generator.url(),
            'id': id,
            'name': generator.user_name(),
            'project': 'my/test-project',
            'revision': 0,
            'raw': {'sbg:id': id}
        }

    def apps_exist(self, visibility, num_of_apps):
        items = [AppProvider.default_app() for _ in range(num_of_apps)]
        if visibility:
            url = f'/apps?visibility={visibility}'
        else:
            url = '/apps'
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_apps)})

    def app_exist_non_json(self, status_code):
        url = '/apps'
        href = self.base_url + url

        response = generator.user_name()
        self.request_mocker.get(
            href,
            status_code=status_code,
            text=response
        )

    def app_with_revision_exists(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        href = f'/apps/{app["id"]}/{app["revision"]}'
        self.request_mocker.get(href, json=app)

    def apps_exist_for_project(self, project, num_of_apps):
        items = [AppProvider.default_app() for _ in range(num_of_apps)]
        href = f'{self.base_url}/apps?project={project}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_apps)})

    def app_can_be_copied(self, **kwargs):
        app = self.default_app()
        app['id'] = kwargs.pop('id')
        app['name'] = kwargs.pop('new_name')
        href = f'/apps/{app["id"]}/actions/copy'
        self.request_mocker.request('POST', url=href, json=app)

    def app_exists(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        id = app['id']
        app['raw']['id'] = id
        href = f'/apps/{id}'
        self.request_mocker.get(url=href, json=app)

    def app_can_be_installed(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        app['raw']['sbg:id'] = app['id']
        href = f'/apps/{app["id"]}/raw'
        self.request_mocker.request('POST', url=href, json=app['raw'])

    def revision_can_be_created(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        app['raw']['sbg:id'] = app['id']
        href = f'/apps/{app["id"]}/{app["revision"]}/raw'
        self.request_mocker.request('POST', url=href, json=app['raw'])


class TaskProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_task():
        id = generator.uuid4()
        task = {
            'href': generator.url(),
            'id': id,
            'name': generator.user_name(),
            'project': 'my/test-project',
            'app': 'my/test-project/test/0',
            'status': 'DRAFT',
            'inputs': {
                "FASTQ_Reads": [
                    {
                        "path": "52d69fc0e4b0a77ec4fd2064",
                        "class": "File",
                        "name": "example_human_Illumina.pe_1.fastq"
                    },
                    {
                        "path": "52d69fc0e4b0a77ec4fd2063",
                        "class": "File",
                        "name": "example_human_Illumina.pe_2.fastq"
                    }
                ],
                "test": 1,
                'FastQC_file': {
                    "path": "52d69fc0e4b0a77ec4fd2064",
                    "class": "File",
                    "name": "example_human_Illumina.pe_1.fastq"
                }
            }
        }
        task['outputs'] = task['inputs']
        return task

    def exists(self, **kwargs):
        task = TaskProvider.default_task()
        task.update(**kwargs)
        url = f'{self.base_url}/tasks/{task["id"]}'
        self.request_mocker.get(url, json=task)
        return task

    def exist(self, tasks):
        all_tasks = []
        for task_data in tasks:
            task = TaskProvider.default_task()
            task.update(task_data)
            id_ = task['id']
            href = f'{task["href"]}tasks/{id_}'
            task['href'] = href
            self.request_mocker.get(f'/tasks/{id_}', json=task)
            all_tasks.append({'resource': task})

        data = {'items': all_tasks}
        self.request_mocker.post('/bulk/tasks/get', json=data)

    @staticmethod
    def execution_details():
        return {
            'href': generator.url(),
            'status': generator.name(),
            'jobs': [
                {
                    "name": generator.name(),
                }
            ]
        }

    def tasks_exists_for_project(self, project, num_of_tasks):
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
        href = f'{self.base_url}/tasks?project={project}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_tasks)})

    def tasks_in_project_for_parent(self, project, parent, num_of_tasks):
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
        href = f'{self.base_url}/tasks?project={project}&parent={parent}'
        href_no_parent = f'{self.base_url}/tasks?project={project}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }

        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_tasks)})
        self.request_mocker.get(href_no_parent, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_tasks)})

    def tasks_in_project(self, project, num_of_tasks):
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
        href = f'{self.base_url}/tasks?project={project}'

        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }

        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_tasks)})

    def tasks_exist_for_parent(self, parent, num_of_tasks):
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
        href = f'{self.base_url}/tasks?parent={parent}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num_of_tasks)})

    def can_be_created(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        href = '/tasks'
        self.request_mocker.request('POST', href, json=task)

    def created_with_errors(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        task['errors'] = [{'error': 'some_error'}]
        href = '/tasks'
        self.request_mocker.request('POST', href, json=task)

    def task_exists(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        id = task['id']
        href = f'{task["href"]}tasks/{id}'
        task['href'] = href
        self.request_mocker.get(f'/tasks/{id}', json=task)

    def task_can_be_aborted(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        id = task['id']
        self.request_mocker.request(
            'POST', f'/tasks/{id}/actions/abort', json=task
        )

    def task_can_be_run(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        id = task['id']
        self.request_mocker.request(
            'POST', f'/tasks/{id}/actions/run', json=task
        )

    def task_can_be_clone(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        id = task['id']
        self.request_mocker.request(
            'POST', f'/tasks/{id}/actions/clone', json=task
        )

    def task_can_be_saved(self, id=None, status=None):
        task = TaskProvider.default_task()
        task['id'] = id
        task['status'] = status
        self.request_mocker.patch(f'/tasks/{id}', json=task)

    def task_execution_details_exist(self, id=None):
        execution_details = TaskProvider.execution_details()
        self.request_mocker.get(
            f'/tasks/{id}/execution_details',
            json=execution_details
        )


class VolumeProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.member_provider = MemberProvider(request_mocker, base_url)

    @staticmethod
    def default_volume():
        volume = {
            "href": generator.url(),
            "id": 'my/my-volume',
            "name": generator.name(),
            "description": "Awesome!",
            "access_mode": "RO",
            "service": {
                "type": "GCS",
                "bucket": "test",
                "prefix": "",
                "root_url": "https://www.googleapis.com/",
                "credentials": {
                    "client_email": "test@test.com"
                }
            }
        }
        return volume

    def can_be_queried(self, num):
        items = [VolumeProvider.default_volume() for _ in range(num)]
        href = f'{self.base_url}/storage/volumes'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(num)})

    def volume_created(self, name):
        volume = VolumeProvider.default_volume()
        volume['name'] = name
        self.request_mocker.request('POST', '/storage/volumes', json=volume)

    def exist(self, **kwargs):
        volume = VolumeProvider.default_volume()
        volume.update(kwargs)
        url = f'{self.base_url}/storage/volumes/{volume["id"]}'
        self.request_mocker.get(url, json=volume)

    def can_be_modified(self, **kwargs):
        volume = VolumeProvider.default_volume()
        volume.update(kwargs)
        url = f'{self.base_url}/storage/volumes/{volume["id"]}'
        self.request_mocker.patch(url, json=volume)

    def paginated_file_list(self, limit, num_of_files, volume_id, volume_data):
        all_items = [
            {
                'href': f'{self.base_url}/storage/volumes/{volume_id}/list',
                'location': generator.uuid4(),
                'volume': volume_id,
                'type': 's3'
            } for _ in range(num_of_files)
        ]

        all_links = []
        for i in range(0, num_of_files, limit):
            href = (
                f'{self.base_url}/storage/volumes/{volume_id}'
                f'/list/?offset={i}&limit={limit}'
            )
            items = all_items[i:i + limit]

            links = []
            if i + limit < num_of_files:
                next_page_link = {
                    'next':  (
                        f'{self.base_url}/storage/volumes/{volume_id}/list/'
                        f'?offset={i + limit}&limit={limit}&fields=_all'
                    )
                }
                links.append(next_page_link)

            all_links.append(links)
            response = {
                'href': href,
                'items': items,
                'links': links,
                'prefixes': []
            }
            self.request_mocker.get(href, json=response, headers={
                TOTAL_MATCH_HEADER: str(num_of_files)})

        volume = VolumeProvider.default_volume()
        volume.update(volume_data)

        url = f'{self.base_url}/storage/volumes/{volume["id"]}'
        self.request_mocker.get(url, json=volume)

        list_url = f'{self.base_url}/storage/volumes/{volume["id"]}/list'
        list_data = {
            'href': list_url,
            'items': all_items[:limit],
            'links': all_links[0],
            'prefixes': []
        }
        self.request_mocker.get(list_url, json=list_data)

    def has_member(self, id, member_username):
        member = self.member_provider.default_member(
            username=member_username,
            volume=id
        )
        self.request_mocker.get(
            f'{self.base_url}/storage/volumes/{id}/members/{member_username}',
            json=member
        )


class MarkerProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_marker():
        volume = {
            "href": generator.url(),
            "id": generator.uuid4(),
            "name": generator.name(),
            "file": generator.uuid4(),
            "chromosome": "chr1",
            "position": {
                "start": 2,
                "end": 3
            }
        }
        return volume

    def query(self, total, file):
        items = [MarkerProvider.default_marker() for _ in range(10)]
        href = f'{self.base_url}/genome/markers?file={file}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def created(self, **kwargs):
        marker = MarkerProvider.default_marker()
        marker.update(**kwargs)
        self.request_mocker.request('POST', '/genome/markers', json=marker)

    def exists(self, **kwargs):
        marker = MarkerProvider.default_marker()
        marker.update(**kwargs)
        url = f'{self.base_url}/genome/markers/{marker["id"]}'
        self.request_mocker.get(url, json=marker)

    def modified(self, **kwargs):
        marker = MarkerProvider.default_marker()
        marker.update(**kwargs)
        url = f'{self.base_url}/genome/markers/{marker["id"]}'
        self.request_mocker.patch(url, json=marker)


class ActionProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_copy_result():
        copy_result = {
            'id': {
                "status": "ok",
                "new_file_id": "2",
                "new_file_name": "test"
            }
        }
        return copy_result

    def feedback_set(self):
        url = f'{self.base_url }/action/notifications/feedback'
        self.request_mocker.post(url)

    def can_bulk_copy(self, **kwargs):
        result = self.default_copy_result()
        result.update(kwargs)
        url = f'{self.base_url }/action/files/copy'
        self.request_mocker.post(url, json=result)


class DivisionProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.member_provider = MemberProvider(request_mocker, base_url)

    @staticmethod
    def default_division():
        return {
            'href': generator.url(),
            'id': 'my/my-project',
            'name': generator.user_name(),
        }

    def exists(self, **kwargs):
        division = self.default_division()
        division.update(kwargs)
        id = division['id']
        self.request_mocker.get(f'/divisions/{id}', json=division)

    def query(self, total):
        items = [DivisionProvider.default_division() for _ in range(total)]
        url = '/divisions'
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def teams_exist(self, id, total):
        items = [TeamProvider.default_team() for _ in range(total)]
        href = f'{self.base_url}/teams?division={id}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def members_exist(self, id, total):
        items = [self.member_provider.default_member() for _ in range(total)]
        href = f'{self.base_url}/users?division={id}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})


class TeamProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_team():
        return {
            'href': generator.url(),
            'id': 'my/my-project',
            'name': generator.user_name(),
        }

    def exists(self, **kwargs):
        team = self.default_team()
        team.update(kwargs)
        id = team['id']
        self.request_mocker.get(f'/teams/{id}', json=team)

    def query(self, total):
        items = [TeamProvider.default_team() for _ in range(total)]
        href = f'{self.base_url}/teams'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def created(self, name):
        team = TeamProvider.default_team()
        team['name'] = name
        self.request_mocker.request('POST', '/teams', json=team)

    def modified(self, **kwargs):
        team = TeamProvider.default_team()
        team.update(kwargs)
        self.request_mocker.patch(f'/teams/{team["id"]}', json=team)


class TeamMemberProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def default_member(self, id, username=None):
        if username is None:
            username = generator.user_name()
        url = f'{self.base_url}/team/{id}/members/{username}'
        return {
            'href': url,
            'username': username,
            'permissions': {
                'write': True,
                'read': True,
                'admin': False,
                'copy': False
            }
        }

    def queried(self, team, total=10):
        items = [self.default_member(team) for _ in range(total)]
        href = f'{self.base_url}/teams/{team}/members'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})


class ImportsProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_import():
        return {
            "id": generator.uuid4(),
            "href": generator.url(),
            "state": generator.name(),
            "overwrite": False
        }

    def query(self, total):
        items = [ImportsProvider.default_import() for _ in range(total)]
        href = f'{self.base_url}/storage/imports'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def can_be_submitted(self, **kwargs):
        imports = self.default_import()
        imports.update(kwargs)
        self.request_mocker.post('/storage/imports', json=imports)

    def can_be_retrieved_in_bulk(self, imports_data):
        imports = []
        for import_data in imports_data:
            import_ = self.default_import()
            import_.update(import_data)
            imports.append({'resource': import_})

        data = {'items': imports}
        self.request_mocker.post('/bulk/storage/imports/get', json=data)

    def can_be_submitted_in_bulk(self, imports_data):
        imports = []
        for import_data in imports_data:
            import_ = {
                'source': {
                    'volume': import_data.get('volume'),
                    'location': import_data.get('location'),
                },
                'destination': {
                    'project': import_data.get('project'),
                },
                'overwrite': import_data.get('overwrite', False)
            }

            name = import_data.get('name')
            if name:
                import_['destination']['name'] = name

            imports.append({'resource': import_})

        data = {'items': imports}
        self.request_mocker.post('/bulk/storage/imports/create', json=data)


class ExportsProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_export():
        return {
            "id": generator.uuid4(),
            "href": generator.url(),
            "state": generator.name(),
            "destination": generator.name()
        }

    def query(self, total):
        items = [self.default_export() for _ in range(total)]
        href = f'{self.base_url}/storage/exports'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def can_be_submitted(self, **kwargs):
        exports = self.default_export()
        exports.update(kwargs)
        self.request_mocker.post('/storage/exports', json=exports)

    def can_be_retrieved_in_bulk(self, exports_data):
        exports = []
        for export_data in exports_data:
            export = self.default_export()
            export.update(export_data)
            exports.append({'resource': export})

        data = {'items': exports}
        self.request_mocker.post('/bulk/storage/exports/get', json=data)

    def can_be_submitted_in_bulk(self, exports_data):
        exports = []
        for export_data in exports_data:
            export = {
                'source': {
                    'file': export_data.get('file')
                },
                'destination': {
                    'volume': export_data.get('volume'),
                    'location': export_data.get('location')
                },
                'properties': export_data.get('properties', {}),
                'overwrite': export_data.get('overwrite', False)
            }
            exports.append({'resource': export})

        data = {'items': exports}
        self.request_mocker.post('/bulk/storage/exports/create', json=data)


class DatasetProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.member_provider = MemberProvider(request_mocker, base_url)

    @staticmethod
    def default_dataset():
        return {
            "id": "my/my-dataset",
            "href": generator.url(),
            "name": generator.name(),
            "description": generator.name(),
        }

    def exists(self, **kwargs):
        dataset = self.default_dataset()
        dataset.update(kwargs)
        id = dataset['id']
        self.request_mocker.get(f'/datasets/{id}', json=dataset)

    def query(self, total):
        items = [self.default_dataset() for _ in range(total)]
        href = f'{self.base_url}/datasets'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def owned_by(self, total, username):
        items = [self.default_dataset() for _ in range(total)]
        href = f'{self.base_url}/datasets/{username}'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def can_be_saved(self, **kwargs):
        dataset = self.default_dataset()
        dataset.update(**kwargs)
        id = dataset['id']
        self.request_mocker.patch(f'/datasets/{id}', json=dataset)

    def has_members(self, id, dataset_name, total):
        items = [
            self.member_provider.default_member(dataset=dataset_name)
            for _ in range(total)
        ]
        href = f'{self.base_url}/datasets/{id}/members'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def has_member(self, id, dataset_name, member_username):
        member = self.member_provider.default_member(
            username=member_username,
            dataset=dataset_name
        )

        href = f'{self.base_url}/datasets/{id}/members/{member_username}'
        self.request_mocker.get(href, json=member)

    def can_remove_member(self, id, member_username):
        href = f'{self.base_url}/datasets/{id}/members/{member_username}'
        self.request_mocker.delete(href)

    def can_add_member(self, id, member_username):
        member = self.member_provider.default_member(id, member_username)
        href = f'{self.base_url}/datasets/{id}/members'
        self.request_mocker.post(href, json=member)


class AutomationProvider:

    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.member_provider = AutomationMemberProvider(
            request_mocker, base_url
        )
        self.package_provider = AutomationPackageProvider(
            request_mocker, base_url
        )
        self.run_provider = AutomationRunProvider(request_mocker, base_url)

    @staticmethod
    def default_automation():
        return {
            'href': generator.url(),
            'id': generator.uuid4(),
            'name': generator.slug(),
            'description': generator.slug(),
            'billing_group': generator.uuid4(),
            'owner': generator.user_name(),
            'created_by': generator.user_name(),
            'created_on': generator.date(),
            'modified_by': generator.user_name(),
            'modified_on': generator.date(),
            'archived': False,
            'project_based': False,
        }

    def exists(self, **kwargs):
        automation = self.default_automation()
        automation.update(kwargs)
        id = automation['id']
        self.request_mocker.get(
            f'/automation/automations/{id}', json=automation
        )

    def can_be_created(self, **kwargs):
        automation = self.default_automation()
        automation.update(**kwargs)
        self.request_mocker.post(
            '/automation/automations', json=automation
        )

    def can_be_saved(self, **kwargs):
        automation = self.default_automation()
        automation.update(**kwargs)
        id = automation['id']
        self.request_mocker.patch(
            f'/automation/automations/{id}', json=automation
        )

    def can_be_archived(self, **kwargs):
        automation = self.default_automation()
        automation['archived'] = True
        automation.update(**kwargs)
        id = automation['id']
        self.request_mocker.post(
            f'/automation/automations/{id}/actions/archive', json=automation
        )

    def can_be_restored(self, **kwargs):
        automation = self.default_automation()
        automation['archived'] = False
        automation.update(**kwargs)
        id = automation['id']
        self.request_mocker.post(
            f'/automation/automations/{id}/actions/restore', json=automation
        )

    def query(self, total):
        items = [self.default_automation() for _ in range(total)]
        href = f'{self.base_url}/automation/automations'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def has_member(self, id, username):
        member = self.member_provider.default_automation_member(
            username=username,
        )
        href = (
            f'{self.base_url}/automation/automations/{id}/members/{username}'
        )
        self.request_mocker.get(href, json=member)

    def has_team_member(self, id, team_id):
        member = self.member_provider.default_automation_team_member(
            team_id=team_id,
        )
        href = (
            f'{self.base_url}/automation/automations/{id}/members/{team_id}'
        )
        self.request_mocker.get(href, json=member)

    def has_members(self, id, total):
        items = [
            self.member_provider.default_automation_member()
            for _ in range(total)
        ]
        href = f'{self.base_url}/automation/automations/{id}/members'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def can_add_member(self, id, username):
        member = self.member_provider.default_automation_member(
            id, username
        )
        href = f'{self.base_url}/automation/automations/{id}/members'
        self.request_mocker.post(href, json=member)

    def can_add_team_member(self, id, team_id):
        member = self.member_provider.default_automation_team_member(
            id, team_id
        )
        href = f'{self.base_url}/automation/automations/{id}/members'
        self.request_mocker.post(href, json=member)

    def can_remove_member(self, id, username):
        href = (
            f'{self.base_url}/automation/automations/{id}/members/{username}'
        )
        self.request_mocker.delete(href)

    def can_remove_team_member(self, id, team_id):
        href = (
            f'{self.base_url}/automation/automations/{id}/members/{team_id}'
        )
        self.request_mocker.delete(href)

    def has_package(self, package_id):
        package = self.package_provider.default_automation_package(
            package_id=package_id
        )
        href = f'{self.base_url}/automation/packages/{package_id}'
        self.request_mocker.get(href, json=package)

    def can_add_package(self, automation_id, package_id,
                        location, version, schema, python):
        package = self.package_provider.default_automation_package(
            package_id=package_id, location=location, version=version,
            schema=schema, python=python
        )
        href = (
            f'{self.base_url}/automation/automations/{automation_id}/packages'
        )
        self.request_mocker.post(href, json=package)

    def has_packages(self, id, total):
        items = [
            self.package_provider.default_automation_package()
            for _ in range(total)
        ]
        href = f'{self.base_url}/automation/automations/{id}/packages'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def has_runs(self, id, total):
        items = [
            self.run_provider.default_automation_run(automation=id)
            for _ in range(total)
        ]
        href = f'{self.base_url}/automation/runs'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})


class AutomationPackageProvider:

    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_automation_package(
            package_id=None, version=None, location=None, schema=None,
            python=None
    ):
        package_id = package_id or generator.uuid4()
        version = version or generator.slug()
        location = location or generator.slug()
        schema = schema or {}

        return {
            'id': package_id,
            'automation': generator.uuid4(),
            'version': version,
            'location': location,
            'schema': schema,
            'created_by': generator.user_name(),
            'created_on': generator.date(),
            'archived': False,
            'custom_url': generator.url(),
            'python': python
        }

    def exists(self, **kwargs):
        package = self.default_automation_package()
        package.update(**kwargs)
        package_id = package['id']
        self.request_mocker.get(
            f'/automation/packages/{package_id}',
            json=package
        )

    def can_be_created(self, **kwargs):
        package = self.default_automation_package()
        automation_id = package['automation']
        [package.pop(key) for key in ['id']]
        package.update(**kwargs)
        self.request_mocker.request(
            'POST', f'/automation/automations/{automation_id}/packages',
            json=package
        )

    def can_be_archived(self, **kwargs):
        package = self.default_automation_package()
        package['archived'] = True
        package.update(**kwargs)
        package_id = package['id']
        automation_id = package['automation']
        self.request_mocker.post(
            f'/automation/automations/{automation_id}'
            f'/packages/{package_id}/actions/archive',
            json=package
        )

    def can_be_restored(self, **kwargs):
        package = self.default_automation_package()
        package['archived'] = False
        package.update(**kwargs)
        package_id = package['id']
        automation_id = package['automation']
        self.request_mocker.post(
            f'/automation/automations/{automation_id}'
            f'/packages/{package_id}/actions/restore',
            json=package
        )

    def can_be_saved(self, **kwargs):
        package = self.default_automation_package()
        package.update(**kwargs)
        id = package['id']
        self.request_mocker.patch(
            f'/automation/packages/{id}', json=package
        )


class AutomationMemberProvider:

    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def default_automation_member(self, automation=None, username=None,
                                  permissions=None):
        username = username or generator.user_name()
        automation = automation or generator.uuid4()
        permissions = permissions or {
            'admin': False,
            'copy': True,
            'read': True,
            'write': True,
            'execute': False,
        }
        url = (
            f'{self.base_url}/automation/automations/{automation}'
            f'/members/{username}'
        )
        return {
            'href': url,
            'username': username,
            'permissions': permissions,
        }

    def default_automation_team_member(self, automation=None, team_id=None,
                                       permissions=None):
        team_id = team_id or generator.generator.uuid4()
        automation = automation or generator.uuid4()
        permissions = permissions or {
            'admin': False,
            'copy': True,
            'read': True,
            'write': True,
            'execute': False,
        }
        url = (
            f'{self.base_url}/automation/automations/{automation}'
            f'/members/{team_id}'
        )
        return {
            'href': url,
            'id': team_id,
            'type': 'TEAM',
            'permissions': permissions,
        }

    def exists(self, **kwargs):
        automation_member = self.default_automation_member(**kwargs)
        automation_member.update(kwargs)
        username = automation_member['username']
        automation = automation_member['automation']
        self.request_mocker.get(
            f'/automation/automations/{automation}/members/{username}',
            json=automation_member
        )

    def can_be_saved(self, automation, **kwargs):
        automation_member = self.default_automation_member()
        automation_member.update(**kwargs)
        username = automation_member['username']
        self.request_mocker.patch(
            f'/automation/automations/{automation}/members/{username}',
            json=automation_member
        )


class AutomationRunProvider:

    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.file_provider = FileProvider(request_mocker, base_url)

    def default_automation_run(self, automation=None):
        automation = automation or generator.uuid4()
        return {
            'href': generator.url(),
            'id': generator.uuid4(),
            'name': generator.name(),
            'automation': automation,
            'package': generator.uuid4(),
            'inputs': {},
            'outputs': None,
            'settings': {},
            'created_on': generator.date(),
            'start_time': generator.date(),
            'end_time': generator.date(),
            'resumed_from': None,
            'created_by': generator.user_name(),
            'status': 'FINISHED',
            'message': generator.slug(),
            'execution_details': {
                'log_file': self.file_provider.default_file(),
                'state_file': self.file_provider.default_file(),
            },
            'project_id': None
        }

    @staticmethod
    def default_state():
        state = {
            'main': {
                'started_at': generator.time(),
                'inputs': {},
                'substeps': {},
                'finished_at': generator.time(),
                'error': {'message': '', 'trace': ''}
            }
        }
        return state

    def exists(self, **kwargs):
        automation_run = self.default_automation_run()
        automation_run.update(kwargs)
        id = automation_run['id']
        self.request_mocker.get(
            f'/automation/runs/{id}', json=automation_run
        )

    def has_rerun(self, **kwargs):
        automation_run = self.default_automation_run()
        automation_run.update(**kwargs)
        self.request_mocker.request(
            'POST',
            f'/automation/runs/{kwargs["id"]}/actions/rerun',
            json=automation_run
        )

    def has_state(self, id, state):
        state = state or self.default_state()
        href = f'{self.base_url}/automation/runs/{id}/state'
        self.request_mocker.get(href, json=state)

    def can_be_created(self, **kwargs):
        automation_run = self.default_automation_run()
        [automation_run.pop(key) for key in ['id', 'href']]
        automation_run.update(**kwargs)
        self.request_mocker.request(
            'POST', '/automation/runs', json=automation_run
        )

    def can_be_stopped(self, id):
        self.request_mocker.request(
            'POST', f'/automation/runs/{id}/actions/stop'
        )

    def query(self, total):
        items = [self.default_automation_run() for _ in range(total)]
        href = f'{self.base_url}/automation/runs'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})


class AsyncJobProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_async_job():
        return {
            'id': generator.uuid4(),
            'type': 'COPY',
            'state': 'SUBMITTED',
            'result': [],
            'total_files': 0,
            'failed_files': 0,
            'completed_files': 0,
            'started_on': generator.time(),
            'finished_on': generator.time(),
        }

    # noinspection PyShadowingBuiltins
    def exists(self, type, **kwargs):
        async_job = self.default_async_job()
        async_job.update(kwargs)
        id = async_job['id']
        self.request_mocker.get(f'/async/files/{type}/{id}', json=async_job)

    def list_file_jobs(self, total):
        items = [self.default_async_job() for _ in range(total)]
        href = f'{self.base_url}/async/files'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            TOTAL_MATCH_HEADER: str(total)})

    def can_copy_files(self, files):
        async_job = self.default_async_job()
        async_job['result'] = [
            {'resource': {'id': file['file']}}
            for file in files
        ]
        self.request_mocker.post(
            '/async/files/copy', json=async_job
        )

    def can_delete_files(self, files):
        async_job = self.default_async_job()
        async_job['result'] = [
            {'resource': {'id': file['file']}}
            for file in files
        ]
        self.request_mocker.post(
            '/async/files/delete', json=async_job
        )

    def can_move_files(self, files):
        async_job = self.default_async_job()
        async_job['result'] = [
            {'resource': {'id': file['file']}}
            for file in files
        ]
        self.request_mocker.post(
            '/async/files/move', json=async_job
        )


class CodePackageUploadProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.file_provider = FileProvider(request_mocker, base_url)

    def initialized_upload(self, upload_id, part_size):
        response = {
            "upload_id": upload_id,
            "part_size": part_size
        }
        self.request_mocker.post(
            f'{self.base_url}/automation/upload', json=response
        )

    def got_file_part(self, url):
        regx = f'^{self.base_url}/automation/upload/.*/part/.*$'
        matcher = re.compile(regx)
        self.request_mocker.get(
            matcher, json={"url": url}
        )

    def got_etag(self, url):
        self.request_mocker.put(
            url,
            json={},
            headers={'etag': generator.uuid4()}
        )

    def reported_part(self):
        regx = f'^{self.base_url}/automation/upload/.*/part/'
        matcher = re.compile(regx)
        self.request_mocker.post(
            matcher, json={}
        )

    def finalized_upload(self, package_file_id):
        regx = f'^{self.base_url}/automation/upload/.*/complete'
        matcher = re.compile(regx)
        self.request_mocker.post(
            matcher, json={"name": "dummy_file_name", "id": package_file_id}
        )

    def deleted(self):
        regx = f'^{self.base_url}/automation/upload/.*'
        matcher = re.compile(regx)
        self.request_mocker.delete(matcher)


class FileUploadProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.file_provider = FileProvider(request_mocker, base_url)

    def initialized_upload(self, upload_id, part_size, failed=False):
        status_code = 500 if failed else 200
        response = {
            "upload_id": upload_id,
            "part_size": part_size
        }
        self.request_mocker.post(
            f'{self.base_url}/upload/multipart',
            json=response,
            status_code=status_code
        )

    def got_file_part(self, url, failed=False):
        status_code = 500 if failed else 200
        regx = f'^{self.base_url}/upload/multipart/.*/part/.*$'
        matcher = re.compile(regx)
        self.request_mocker.get(
            matcher, json={"url": url},
            status_code=status_code
        )

    def got_etag(self, url, failed=False):
        status_code = 500 if failed else 200
        headers = {} if failed else {'etag': generator.uuid4()}

        self.request_mocker.put(
            url,
            json={},
            headers=headers,
            status_code=status_code
        )

    def reported_part(self, failed=False):
        status_code = 500 if failed else 200
        regx = f'^{self.base_url}/upload/multipart/.*/part/'
        matcher = re.compile(regx)
        self.request_mocker.post(
            matcher, json={}, status_code=status_code
        )

    def finalized_upload(self, file_id, failed=False):
        status_code = 500 if failed else 200

        regx = f'^{self.base_url}/upload/multipart/.*/complete'
        matcher = re.compile(regx)
        self.request_mocker.post(
            matcher,
            json={"name": "dummy_file_name", "id": file_id},
            status_code=status_code
        )

    def deleted(self, failed=False):
        status_code = 500 if failed else 200

        regx = f'^{self.base_url}/upload/multipart/.*'
        matcher = re.compile(regx)
        self.request_mocker.delete(matcher, status_code=status_code)


class DRSImportProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_import():
        return {
            'id': generator.uuid4(),
            'href': generator.url(),
            'result': [],
            'state': generator.state(),
            'failed_files': 0,
            'completed_files': 2,
            'total_files': 2,
            'started_on': generator.time(),
            'finished_on': generator.time()
        }

    def can_be_retrieved_in_bulk(self, import_data):
        data = self.default_import()
        data.update(import_data)
        self.request_mocker.get(
            '/bulk/drs/imports/{id}'.format(id=import_data['id']), json=data
        )

    def can_be_submitted_in_bulk(self, imports_data):
        data = self.default_import()
        data['result'] = [
            {'id': generator.uuid4(), 'href': generator.url()}
            for _ in range(len(imports_data))
        ]
        self.request_mocker.post('/bulk/drs/imports/create', json=data)


class BillingGroupProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default() -> dict:
        return {
            'href': generator.url(),
            'id': generator.uuid4(),
            'name': generator.name(),
            'owner': generator.user_name(),
            'type': generator.name(),
            'pending': False,
            'disabled': False,
            'balance': float(generator.pydecimal(positive=True))
        }

    def exist(self, num_of_bg):
        items = [BillingGroupProvider.default() for _ in range(num_of_bg)]

        url = '/billing/groups'
        href = self.base_url + url
        response = {
            'href': href,
            'items': items,
            'links': []
        }
        self.request_mocker.get(
            href, json=response, headers={TOTAL_MATCH_HEADER: str(num_of_bg)}
        )


class BillingGroupStorageBreakdownProvider:
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default() -> dict:
        return {
            'project_name': generator.name(),
            'project_created_by': generator.user_name(),
            'location': generator.name(),
            'active': None,
            'archived': None,
            'project_locked': False
        }

    @staticmethod
    def generate_storage_breakdown() -> dict:
        return {
            'size': str(generator.pydecimal(positive=True)),
            'unit': 'GB/Month',
            'cost': {
                'currency': 'USD',
                'amount': str(generator.pydecimal(positive=True)),
            }
        }

    def exist(self, bg_id, num_of_objects, with_cost=False):
        items = []
        for _ in range(num_of_objects):
            item = BillingGroupStorageBreakdownProvider.default()
            if with_cost:
                item['archived'] = self.generate_storage_breakdown()
                item['active'] = self.generate_storage_breakdown()
            items.append(item)

        url = f'/billing/groups/{bg_id}/breakdown/storage'
        href = self.base_url + url
        response = {
            'href': href,
            'items': items,
            'links': []
        }
        self.request_mocker.get(
            href,
            json=response,
            headers={TOTAL_MATCH_HEADER: str(num_of_objects)}
        )
