import faker

generator = faker.Factory.create()


class EndpointProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def enpoints(self):
        return {
            'rate_limit_url': self.base_url + 'v2/rate_limit',
            'user_url': self.base_url + 'v2/user',
            'users_url': self.base_url + 'v2/users',
            'billing_url': self.base_url + 'v2/billing',
            'projects_url': self.base_url + 'v2/projects',
            'files_url': self.base_url + 'v2/files',
            'tasks_url': self.base_url + 'v2/tasks',
            'apps_url': self.base_url + 'v2/apps',
            'action_url': self.base_url + 'v2/action',
            'upload_url': self.base_url + 'v2/upload'
        }

    def defined(self):
        self.request_mocker.get('/'.format(id), json=self.enpoints())


class UserProvider(object):
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
        self.request_mocker.get('/users/{}'.format(username), json=user)


class ProjectProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_project():
        return {
            'href': generator.url(),
            'id': '{}/{}'.format('my', 'my-project'),
            'name': generator.user_name(),
            'billing_group': generator.uuid4()
        }

    def exists(self, **kwargs):
        project = self.default_project()
        project.update(kwargs)
        id = project['id']
        self.request_mocker.get('/projects/{}'.format(id), json=project)

    def can_be_created(self, **kwargs):
        project = self.default_project()
        [project.pop(key) for key in ['id', 'href']]
        project.update(**kwargs)
        self.request_mocker.request('POST', '/projects', json=project)

    def can_be_saved(self, **kwargs):
        project = self.default_project()
        project.update(**kwargs)
        id = project['id']
        self.request_mocker.patch('/projects/{id}'.format(id=id), json=project)

    def paginated_projects(self, limit, num_of_projects):
        items = [ProjectProvider.default_project() for _ in
                 range(num_of_projects)]
        for i in range(0, num_of_projects, limit):
            href = self.base_url + '/projects?offset={}&limit={}'.format(
                str(i), str(limit)
            )
            sub_items = items[i:i + limit]
            links = []
            if i + limit < num_of_projects:
                next_url = '/projects?offset={offset}&limit={limit}'.format(
                    offset=str(i + limit), limit=str(limit)
                )
                next = {
                    'method': 'GET',
                    'rel': 'next',
                    'href': self.base_url + next_url
                }
                links.append(next)

            if i > limit:
                prev_url = '/projects?offset={offset}&limit={limit}'.format(
                    offset=str(i - limit), limit=str(limit)
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
            self.request_mocker.get(href, json=response, headers={
                'x-total-matching-query': str(num_of_projects)})


class MemberProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def default_member(self, project, username):
        if username is None:
            username = generator.user_name()
        url = self.base_url + '/projects/' + project + "/members/" + username
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
        url = '/projects/{project}/members'.format(
            project=project)
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_members)})

    def member_exist(self, project, username):
        member = self.default_member(project, username)
        member.update({'username': username})
        url = '/projects/{project}/members'.format(
            project=project
        )
        href = self.base_url + url
        self.request_mocker.request('POST', href, json=member)
        return member

    def can_be_removed(self, project, username):
        url = '/projects/{project}/members/{username}'.format(
            project=project, username=username
        )
        href = self.base_url + url
        self.request_mocker.delete(href, status_code=204)

    def permissions_can_be_modified(self, project, username):
        url = '/projects/{project}/members/{username}/permissions'.format(
            project=project, username=username
        )
        href = self.base_url + url
        self.request_mocker.patch(href, status_code=200)


class FileProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_file():
        return {
            'href': generator.url(),
            'id': generator.uuid4(),
            'name': generator.user_name(),
            'project': 'my/test-project',
            'metadata': {
                'sample': generator.name()
            }
        }

    def download_info(self):
        return {
            'url': generator.url()
        }

    def exists(self, **kwargs):
        file = FileProvider.default_file()
        file.update(kwargs)
        id = file['id']
        href = file['href'] + 'files/{}'.format(id)
        file['href'] = href
        self.request_mocker.get('/files/{id}'.format(id=id), json=file)

    def download_info_defined(self, id):
        json = self.download_info()
        url = '/files/{id}/download_info'.format(id=id)
        self.request_mocker.get(url, json=json)

    def can_be_copied(self, id=None, new_id=None):
        file = FileProvider.default_file()
        file['id'] = id
        id = file['id']
        file['id'] = new_id
        self.request_mocker.request(
            'POST', '/files/{id}/actions/copy'.format(id=id), json=file)

    def can_be_saved(self, id=None):
        file = FileProvider.default_file()
        file['id'] = id
        self.request_mocker.patch('/files/{id}'.format(id=id),
                                  json=file)

    def metadata_can_be_saved(self, id):
        file = FileProvider.default_file()
        self.request_mocker.patch(
            '/files/{id}/metadata'.format(id=id), json=file['metadata']
        )

    def files_exist_for_project(self, project, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        href = self.base_url + '/files?project={project}'.format(
            project=project
        )
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_files)})

    def files_exist_for_file_name(self, project, file_name, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        url = '/files?project={project}&name={name}'.format(
            project=project, name=file_name
        )
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_files)})

    def files_exist_for_file_metadata(self, project, key, value, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        url = '/files?project={project}&metadata.{key}={value}'.format(
            project=project, key=key, value=value)
        href = self.base_url + url

        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_files)})

    def files_exist_for_file_origin(self, project, key, value, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        url = '/files?project={project}&origin.{key}={value}'.format(
            project=project, key=key, value=value
        )
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_files)})


class AppProvider(object):
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
            url = '/apps?visibility={visibility}'.format(visibility=visibility)
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
            'x-total-matching-query': str(num_of_apps)})

    def app_with_revision_exists(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        href = '/apps/{}/{}'.format(app['id'], app['revision'])
        self.request_mocker.get(href, json=app)

    def apps_exist_for_project(self, project, num_of_apps):
        items = [AppProvider.default_app() for _ in range(num_of_apps)]
        url = '/apps?project={project}'.format(project=project)
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_apps)})

    def app_can_be_copied(self, **kwargs):
        app = self.default_app()
        app['id'] = kwargs.pop('id')
        app['name'] = kwargs.pop('new_name')
        print(app['id'])
        href = '/apps/{}/actions/copy'.format(app['id'])
        self.request_mocker.request('POST', url=href, json=app)

    def app_exists(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        id = app['id']
        app['raw']['id'] = id
        href = '/apps/{}'.format(id)
        self.request_mocker.get(url=href, json=app)

    def app_can_be_installed(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        app['raw']['sbg:id'] = app['id']
        href = '/apps/{}/raw'.format(app['id'])
        self.request_mocker.request('POST', url=href, json=app['raw'])

    def revision_can_be_created(self, **kwargs):
        app = self.default_app()
        app.update(kwargs)
        app['raw']['sbg:id'] = app['id']
        href = '/apps/{}/{}/raw'.format(
            app['id'], app['revision'], app['revision']
        )
        self.request_mocker.request('POST', url=href, json=app['raw'])


class TaskProvider(object):
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
        items = [AppProvider.default_app() for _ in range(num_of_tasks)]
        project_url = '/tasks?project={project}'.format(project=project)
        href = self.base_url + project_url

        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_tasks)})

    def tasks_in_project_for_parent(self, project, parent, num_of_tasks):
        items = [AppProvider.default_app() for _ in range(num_of_tasks)]
        url = '/tasks?project={project}&parent={parent}'.format(
            project=project, parent=parent
        )
        href = self.base_url + url

        url_no_parent = '/tasks?project={project}'.format(project=project)
        href_no_parent = self.base_url + url_no_parent
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }

        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_tasks)})
        self.request_mocker.get(href_no_parent, json=response, headers={
            'x-total-matching-query': str(num_of_tasks)})

    def tasks_exist_for_parent(self, parent, num_of_tasks):
        items = [AppProvider.default_app() for _ in range(num_of_tasks)]
        url = '/tasks?parent={parent}'.format(parent=parent)
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_tasks)})

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
        href = task['href'] + 'tasks/{}'.format(id)
        task['href'] = href
        self.request_mocker.get('/tasks/{}'.format(id), json=task)

    def task_can_be_aborted(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        id = task['id']
        self.request_mocker.request(
            'POST', '/tasks/{}/actions/abort'.format(id), json=task
        )

    def task_can_be_run(self, **kwargs):
        task = self.default_task()
        task.update(kwargs)
        id = task['id']
        self.request_mocker.request(
            'POST', '/tasks/{}/actions/run'.format(id), json=task
        )

    def task_can_be_saved(self, id=None, status=None):
        task = TaskProvider.default_task()
        task['id'] = id
        task['status'] = status
        self.request_mocker.patch('/tasks/{id}'.format(id=id), json=task)

    def task_execution_details_exist(self, id=None):
        execution_details = TaskProvider.execution_details()
        self.request_mocker.get(
            '/tasks/{id}/execution_details'.format(id=id),
            json=execution_details
        )


class VolumeProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_volume():
        volume = {
            "href": generator.url(),
            "id": '{}/{}'.format('my', 'my-volume'),
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
        href = self.base_url + '/storage/volumes'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num)})

    def volume_created(self, name):
        volume = VolumeProvider.default_volume()
        volume['name'] = name
        self.request_mocker.request('POST', '/storage/volumes', json=volume)

    def exist(self, **kwargs):
        volume = VolumeProvider.default_volume()
        volume.update(kwargs)
        url = self.base_url + '/storage/volumes/{}'.format(volume['id'])
        self.request_mocker.get(url, json=volume)

    def can_be_modified(self, **kwargs):
        volume = VolumeProvider.default_volume()
        volume.update(kwargs)
        url = self.base_url + '/storage/volumes/{}'.format(volume['id'])
        self.request_mocker.patch(url, json=volume)
