import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import SbgError
from sevenbridges.meta.collection import Collection
from sevenbridges.models.app import App
from sevenbridges.models.file import File
from sevenbridges.models.link import Link
from sevenbridges.models.member import Member
from sevenbridges.models.task import Task
from sevenbridges.meta.fields import (
    HrefField, StringField, UuidField, BasicListField
)


class Project(Resource):
    """
    Central resource for managing projects.
    """
    _URL = {
        'query': '/projects',
        'get': '/projects/{id}',
        'delete': '/projects/{id}',
        'members_query': '/projects/{id}/members',
        'members_get': '/projects/{id}/members/{member}',
        'apps': '/apps',
        'files': '/files',
        'tasks': '/tasks'
    }
    href = HrefField()
    id = StringField(read_only=False)
    name = StringField(read_only=False)
    billing_group = UuidField(read_only=False)
    description = StringField(read_only=False)
    type = StringField(read_only=False, max_length=2)
    tags = BasicListField(read_only=False)

    def __str__(self):
        return six.text_type('<Project: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, offset=None, limit=None, api=None):
        """
        Query (List) projects
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api if api else cls._API
        return super(Project, cls)._query(url=cls._URL['query'], offset=offset,
                                          limit=limit, api=api)

    @classmethod
    def create(cls, name, billing_group, description=None, tags=None,
               api=None):
        """
        Create a project.
        :param name:  Project name.
        :param billing_group: Project billing group.
        :param description:  Project description.
        :param tags: Project tags.
        :param api: Api instance.
        :return:
        """
        api = api if api else cls._API

        billing_group = Transform.to_billing_group(billing_group)
        if name is None:
            raise SbgError('Project name is required!')

        data = {
            'name': name,
            'billing_group': billing_group,
        }
        if description:
            data['description'] = description
        if tags:
            data['tags'] = tags

        project_data = api.post(url=cls._URL['query'],
                                data=data).json()
        return Project(api=api, **project_data)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the project on the server.
        :param inplace Apply edits on the current instance or get a new one.
        :return: Project instance.
        """
        if bool(self._modified_data()):
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=self._modified_data()).json()
            project = Project(api=self._api, **data)
            return project

    def get_members(self, offset=None, limit=None):
        """
        Retrieves project members.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        response = self._api.get(
            url=self._URL['members_query'].format(id=self.id),
            params={'offset': offset, 'limit': limit})
        data = response.json()
        total = response.headers['x-total-matching-query']
        members = [Member(api=self._api, **member) for member in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(resource=Member, href=href, total=total,
                          items=members, links=links, api=self._api)

    def add_member(self, user, permissions):
        """
        Add a member to the project.
        :param user:  Member username
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        user = Transform.to_user(user)
        data = {}
        if isinstance(permissions, dict):
            data = {
                'username': user,
                'permissions': permissions
            }
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def get_files(self, offset=None, limit=None):
        """
        Retrieves files in this project.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        response = self._api.get(url=self._URL['files'],
                                 params={'project': self.id, 'offset': offset,
                                         'limit': limit})
        data = response.json()
        total = response.headers['x-total-matching-query']
        files = [File(api=self._api, **file) for file in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(resource=File, href=href, total=total, items=files,
                          links=links, api=self._api)

    def add_files(self, files):
        """
        Adds files to this project.
        :param files: List of files or a Collection object.
        """
        for file in files:
            file.copy(project=self.id)

    def get_apps(self, offset=None, limit=None):
        """
        Retrieves apps in this project.
        :param offset:  Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        response = self._api.get(url=self._URL['apps'],
                                 params={'project': self.id, 'offset': offset,
                                         'limit': limit})
        data = response.json()
        total = response.headers['x-total-matching-query']
        apps = [App(api=self._api, **app) for app in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(resource=App, href=href, total=total, items=apps,
                          links=links, api=self._api)

    def get_tasks(self, offset=None, limit=None):
        """
        Retrieves tasks in this project.
        :param offset:  Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        response = self._api.get(url=self._URL['tasks'],
                                 params={'project': self.id, 'offset': offset,
                                         'limit': limit})
        data = response.json()
        total = response.headers['x-total-matching-query']
        tasks = [Task(api=self._api, **task) for task in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(resource=Task, href=href, total=total, items=tasks,
                          links=links, api=self._api)

    def remove_member(self, user):
        """
        Remove member from the project.
        :param user: User to be removed.
        """
        member = Transform.to_user(user)
        self._api.delete(url=self._URL['members_get'].format(
            id=self.id,
            member=member))
