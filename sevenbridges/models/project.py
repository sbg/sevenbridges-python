import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import SbgError, ResourceNotModified
from sevenbridges.meta.collection import Collection
from sevenbridges.models.compound.projects.settings import Settings
from sevenbridges.models.link import Link
from sevenbridges.models.member import Member
from sevenbridges.meta.fields import (
    HrefField, StringField, UuidField, BasicListField,
    CompoundField)


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
    id = StringField(read_only=True)
    name = StringField(read_only=False)
    billing_group = UuidField(read_only=False)
    description = StringField(read_only=False)
    type = StringField(read_only=False, max_length=2)
    tags = BasicListField(read_only=False)
    settings = CompoundField(Settings, read_only=False)

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
        return super(Project, cls)._query(
            url=cls._URL['query'], offset=offset, limit=limit, fields='_all',
            api=api
        )

    @classmethod
    def create(cls, name, billing_group, description=None, tags=None,
               settings=None, api=None):
        """
        Create a project.
        :param name:  Project name.
        :param billing_group: Project billing group.
        :param description:  Project description.
        :param tags: Project tags.
        :param settings: Project settings.
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

        if settings:
            data['settings'] = settings

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
        else:
            raise ResourceNotModified()

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
        params = {'project': self.id, 'offset': offset, 'limit': limit}
        return self._api.files.query(api=self._api, **params)

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
        params = {'project': self.id, 'offset': offset,
                  'limit': limit}
        return self._api.apps.query(api=self._api, **params)

    def get_tasks(self, status=None, offset=None, limit=None):
        """
        Retrieves tasks in this project.
        :param status: Optional task status.
        :param offset:  Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        params = {'project': self.id, 'offset': offset, 'limit': limit}
        if status:
            params['status'] = status
        return self._api.tasks.query(api=self._api, **params)

    def get_imports(self, volume=None, state=None, offset=None, limit=None):
        """
        Fetches imports for this project.
        :param volume: Optional volume identifier.
        :param state: Optional state.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        return self._api.imports.query(project=self.id, volume=volume,
                                       state=state, offset=offset, limit=limit)

    def get_exports(self, volume=None, state=None, offset=None, limit=None):
        """
        Fetches exports for this volume.
        :param volume: Optional volume identifier.
        :param state: Optional state.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        return self._api.exports.query(project=self.id, volume=volume,
                                       state=state, offset=offset, limit=limit)

    def remove_member(self, user):
        """
        Remove member from the project.
        :param user: User to be removed.
        """
        member = Transform.to_user(user)
        self._api.delete(
            url=self._URL['members_get'].format(id=self.id, member=member)
        )
