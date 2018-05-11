import time

import faker

generator = faker.Factory.create()


class EndpointProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def endpoints(self):
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
        self.request_mocker.get('/'.format(id), json=self.endpoints())


class RateLimitProvider(object):
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
            href = self.base_url + '/projects/?offset={}&limit={}'.format(
                str(i), str(limit)
            )
            sub_items = items[i:i + limit]
            links = []
            if i + limit < num_of_projects:
                url = '/projects/?offset={offset}&limit={limit}&fields=_all'
                next_url = url.format(
                    offset=str(i + limit), limit=str(limit)
                )
                next = {
                    'method': 'GET',
                    'rel': 'next',
                    'href': self.base_url + next_url
                }
                links.append(next)

            if i > limit:
                url = '/projects/?offset={offset}&limit={limit}&fields=_all'
                prev_url = url.format(
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

    def default_member(self, project=None, username=None, dataset=None):
        if username is None:
            username = generator.user_name()

        if dataset is not None:
            url = (
                self.base_url + '/datasets/' + dataset + "/members/" + username
            )
        else:
            project = project or generator.name()
            url = (
                self.base_url + '/projects/' + project + "/members/" + username
            )

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

    def member_exist(self, project, username=None, email=None):
        member = self.default_member(project, username)
        if username:
            member.update({'username': username})
        if email:
            member.update({'email': email})
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
            },
            'tags': [
                generator.name()
            ]
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
        href = file_['href'] + 'files/{}'.format(id_)
        file_['href'] = href
        self.request_mocker.get('/files/{id}'.format(id=id_), json=file_)

    def exist(self, files):
        all_files = []
        for file_data in files:
            file_ = FileProvider.default_file()
            file_.update(file_data)
            id_ = file_['id']
            href = file_['href'] + 'files/{}'.format(id_)
            file_['href'] = href
            self.request_mocker.get('/files/{id}'.format(id=id_), json=file_)
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
        url = '/files/{id}/download_info'.format(id=id)
        self.request_mocker.get(url, json=json)

    def can_be_copied(self, id=None, new_id=None):
        file_ = FileProvider.default_file()
        file_['id'] = id
        id = file_['id']
        file_['id'] = new_id
        self.request_mocker.request(
            'POST', '/files/{id}/actions/copy'.format(id=id), json=file_)

    def can_be_saved(self, id=None):
        file_ = FileProvider.default_file()
        file_['id'] = id
        self.request_mocker.patch('/files/{id}'.format(id=id),
                                  json=file_)

    def metadata_can_be_saved(self, id):
        file_ = FileProvider.default_file()
        self.request_mocker.patch(
            '/files/{id}/metadata'.format(id=id), json=file_['metadata']
        )

    def tags_can_be_saved(self, id):
        file_ = FileProvider.default_file()
        self.request_mocker.request(
            'PUT', '/files/{id}/tags'.format(id=id), json=file_['tags']
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

    def files_exist_for_file_tag(self, project, tags, num_of_files):
        items = [FileProvider.default_file() for _ in range(num_of_files)]
        url = '/files?project={project}&tag={tag1}&tag={tag2}'.format(
            project=project, tag1=tags[0], tag2=tags[1]
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
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
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
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
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

    def tasks_in_project(self, project, num_of_tasks):
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
        url = '/tasks?project={project}'.format(
            project=project
        )
        href = self.base_url + url

        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }

        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(num_of_tasks)})

    def tasks_exist_for_parent(self, parent, num_of_tasks):
        items = [TaskProvider.default_task() for _ in range(num_of_tasks)]
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

    def paginated_file_list(self, limit, num_of_files, volume_id, volume_data):
        all_items = [
            {
                'href': (
                    self.base_url +
                    '/storage/volumes/{}/list'
                    .format(volume_id)
                ),
                'location': generator.uuid4(),
                'volume': volume_id,
                'type': 's3'
            } for _ in range(num_of_files)
        ]

        all_links = []
        for i in range(0, num_of_files, limit):
            href = (
                self.base_url +
                '/storage/volumes/{id}/list/?offset={offset}&limit={limit}'
                .format(id=volume_id, offset=str(i), limit=str(limit))
            )
            items = all_items[i:i + limit]

            links = []
            if i + limit < num_of_files:
                next_url = (
                    '/storage/volumes/{id}/list/'
                    '?offset={offset}&limit={limit}&fields=_all'
                    .format(
                        id=volume_id, offset=str(i + limit), limit=str(limit)))
                next_page_link = {
                    'next': self.base_url + next_url
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
                'x-total-matching-query': str(num_of_files)})

        volume = VolumeProvider.default_volume()
        volume.update(volume_data)

        url = self.base_url + '/storage/volumes/{}'.format(volume['id'])
        self.request_mocker.get(url, json=volume)

        list_url = (
            self.base_url + '/storage/volumes/{}/list'.format(volume['id']))
        list_data = {
            'href': list_url,
            'items': all_items[:limit],
            'links': all_links[0],
            'prefixes': []
        }
        self.request_mocker.get(list_url, json=list_data)


class MarkerProvider(object):
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
        href = self.base_url + '/genome/markers?file={}'.format(file)
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

    def created(self, **kwargs):
        marker = MarkerProvider.default_marker()
        marker.update(**kwargs)
        self.request_mocker.request('POST', '/genome/markers', json=marker)

    def exists(self, **kwargs):
        marker = MarkerProvider.default_marker()
        marker.update(**kwargs)
        url = self.base_url + '/genome/markers/{}'.format(marker['id'])
        self.request_mocker.get(url, json=marker)

    def modified(self, **kwargs):
        marker = MarkerProvider.default_marker()
        marker.update(**kwargs)
        url = self.base_url + '/genome/markers/{}'.format(marker['id'])
        self.request_mocker.patch(url, json=marker)


class ActionProvider(object):
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
        url = self.base_url + "/action/notifications/feedback"
        self.request_mocker.post(url)

    def can_bulk_copy(self, **kwargs):
        result = self.default_copy_result()
        result.update(kwargs)
        url = self.base_url + "/action/files/copy"
        self.request_mocker.post(url, json=result)


class DivisionProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_division():
        return {
            'href': generator.url(),
            'id': '{}/{}'.format('my', 'my-project'),
            'name': generator.user_name(),
        }

    def exists(self, **kwargs):
        division = self.default_division()
        division.update(kwargs)
        id = division['id']
        self.request_mocker.get('/divisions/{}'.format(id), json=division)

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
            'x-total-matching-query': str(total)})

    def teams_exist(self, id, total):
        items = [TeamProvider.default_team() for _ in range(total)]
        url = '/teams?division={}'.format(id)
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})


class TeamProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    @staticmethod
    def default_team():
        return {
            'href': generator.url(),
            'id': '{}/{}'.format('my', 'my-project'),
            'name': generator.user_name(),
        }

    def exists(self, **kwargs):
        team = self.default_team()
        team.update(kwargs)
        id = team['id']
        self.request_mocker.get('/teams/{}'.format(id), json=team)

    def query(self, total):
        items = [TeamProvider.default_team() for _ in range(total)]
        url = '/teams'
        href = self.base_url + url
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

    def created(self, name):
        team = TeamProvider.default_team()
        team['name'] = name
        self.request_mocker.request('POST', '/teams', json=team)

    def modified(self, **kwargs):
        team = TeamProvider.default_team()
        team.update(kwargs)
        self.request_mocker.patch('/teams/{}'.format(team['id']), json=team)


class TeamMemberProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url

    def default_member(self, id, username=None):
        if username is None:
            username = generator.user_name()
        url = self.base_url + '/team/{}/members/{}'.format(id, username)
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
        href = self.base_url + '/teams/{}/members'.format(team)
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})


class ImportsProvider(object):
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
        href = self.base_url + '/storage/imports'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

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


class ExportsProvider(object):
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
        href = self.base_url + '/storage/exports'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

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


class DatasetProvider(object):
    def __init__(self, request_mocker, base_url):
        self.request_mocker = request_mocker
        self.base_url = base_url
        self.member_provider = MemberProvider(request_mocker, base_url)

    @staticmethod
    def default_dataset():
        return {
            "id": "{}/{}".format("my", "my-dataset"),
            "href": generator.url(),
            "name": generator.name(),
            "description": generator.name(),
        }

    def exists(self, **kwargs):
        dataset = self.default_dataset()
        dataset.update(kwargs)
        id = dataset['id']
        self.request_mocker.get('/datasets/{}'.format(id), json=dataset)

    def query(self, total):
        items = [self.default_dataset() for _ in range(total)]
        href = self.base_url + '/datasets'
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

    def owned_by(self, total, username):
        items = [self.default_dataset() for _ in range(total)]
        href = self.base_url + '/datasets/' + username
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

    def can_be_saved(self, **kwargs):
        dataset = self.default_dataset()
        dataset.update(**kwargs)
        id = dataset['id']
        self.request_mocker.patch('/datasets/{id}'.format(id=id), json=dataset)

    def has_members(self, id, dataset_name, total):
        items = [
            self.member_provider.default_member(dataset=dataset_name)
            for _ in range(total)
        ]
        href = self.base_url + '/datasets/{}/members'.format(id)
        links = []
        response = {
            'href': href,
            'items': items,
            'links': links
        }
        self.request_mocker.get(href, json=response, headers={
            'x-total-matching-query': str(total)})

    def has_member(self, id, dataset_name, member_username):
        member = self.member_provider.default_member(
            username=member_username,
            dataset=dataset_name
        )

        href = (
            self.base_url +
            '/datasets/{}/members/{}'.format(id, member_username)
        )
        self.request_mocker.get(href, json=member)

    def can_remove_member(self, id, member_username):
        href = (
            self.base_url +
            '/datasets/{}/members/{}'.format(id, member_username)
        )
        self.request_mocker.delete(href)

    def can_add_member(self, id, member_username):
        member = self.member_provider.default_member(id, member_username)
        href = self.base_url + '/datasets/{}/members'.format(id)
        self.request_mocker.post(href, json=member)
