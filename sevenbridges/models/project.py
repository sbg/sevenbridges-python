import logging

import six

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import SbgError, ResourceNotModified
from sevenbridges.meta.collection import Collection
from sevenbridges.meta.fields import (
    HrefField, StringField, UuidField, BasicListField,
    CompoundField, DateTimeField)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.projects.settings import Settings
from sevenbridges.models.link import Link
from sevenbridges.models.member import Member

logger = logging.getLogger(__name__)


class Project(Resource):
    """
    Central resource for managing projects.
    """
    _URL = {
        'query': '/projects/{owner}',
        'create': '/projects',
        'get': '/projects/{id}',
        'delete': '/projects/{id}',
        'member': '/projects/{id}/members/{username}',
        'members_query': '/projects/{id}/members',
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
    root_folder = StringField(read_only=True)
    created_by = StringField(read_only=True)
    created_on = DateTimeField(read_only=True)
    modified_on = DateTimeField(read_only=True)

    def __str__(self):
        return six.text_type('<Project: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def query(cls, owner=None, name=None, offset=None, limit=None, api=None):
        """
        Query (List) projects
        :param owner: Owner username.
        :param name: Project name
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api if api else cls._API
        query_params = {}
        if owner:
            url = cls._URL['query'].format(owner=owner)
        else:
            url = cls._URL['query'].format(owner='')
        if name:
            query_params['name'] = name
        return super(Project, cls)._query(
            url=url, offset=offset, limit=limit, fields='_all',
            api=api, **query_params
        )

    @classmethod
    def create(cls, name, billing_group=None, description=None, tags=None,
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

        if name is None:
            raise SbgError('Project name is required!')

        data = {
            'name': name,
        }

        if billing_group:
            data['billing_group'] = Transform.to_billing_group(billing_group)

        if description:
            data['description'] = description
        if tags:
            data['tags'] = tags

        if settings:
            data['settings'] = settings

        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Creating project', extra=extra)
        project_data = api.post(url=cls._URL['create'], data=data).json()
        return Project(api=api, **project_data)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the project on the server.
        :param inplace Apply edits on the current instance or get a new one.
        :return: Project instance.
        """
        modified_data = self._modified_data()
        if bool(modified_data):
            extra = {
                'resource': self.__class__.__name__,
                'query': {
                    'id': self.id,
                    'modified_data': modified_data
                }
            }
            logger.info('Saving project', extra=extra)
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=modified_data).json()
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
        extra = {
            'resource': self.__class__.__name__,
            'query': {'id': self.id}
        }
        logger.info('Get members', extra=extra)
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
        data = {'username': user, 'type': 'USER'}
        if isinstance(permissions, dict):
            data.update({
                'permissions': permissions
            })

        extra = {
            'resource': self.__class__.__name__,
            'query': {
                'id': self.id,
                'data': data,
            }
        }
        logger.info('Adding member using username', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def add_member_team(self, team, permissions):
        """
        Add a member (team) to a project.
        :param team: Team object or team identifier.
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        team = Transform.to_team(team)
        data = {'id': team, 'type': 'TEAM'}
        if isinstance(permissions, dict):
            data.update({
                'permissions': permissions
            })

        extra = {
            'resource': self.__class__.__name__,
            'query': {
                'id': self.id,
                'data': data,
            }
        }
        logger.info('Adding team member using team id', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def add_member_division(self, division, permissions):
        """
        Add a member (team) to a project.
        :param division: Division object or division identifier.
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        division = Transform.to_division(division)
        data = {'id': division, 'type': 'DIVISION'}
        if isinstance(permissions, dict):
            data.update({
                'permissions': permissions
            })

        extra = {
            'resource': self.__class__.__name__,
            'query': {
                'id': self.id,
                'data': data,
            }
        }
        logger.info('Adding team member using division id', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def add_member_email(self, email, permissions=None):
        """
        Add a member to the project using member email.
        :param email: Member email.
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        data = {'email': email}

        if isinstance(permissions, dict):
            data.update({
                'permissions': permissions
            })

        extra = {
            'resource': self.__class__.__name__,
            'query': {
                'id': self.id,
                'data': data,
            }
        }
        logger.info('Adding member using email', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def get_member(self, username, api=None):
        """
        Fetches information about a single project member
        :param username: Member name
        :param api: Api instance
        :return: Member object
        """
        api = api if api else self._API

        response = api.get(
            url=self._URL['member'].format(id=self.id, username=username),
        )
        data = response.json()
        return Member(api=api, **data)

    def remove_member(self, user):
        """
        Remove member from the project.
        :param user: User to be removed.
        """
        username = Transform.to_user(user)
        extra = {
            'resource': self.__class__.__name__,
            'query': {
                'id': self.id,
                'user': user,
            }
        }
        logger.info('Removing member', extra=extra)
        self._api.delete(
            url=self._URL['member'].format(id=self.id, username=username)
        )

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

    def create_task(self, name, app, revision=None, batch_input=None,
                    batch_by=None, inputs=None, description=None, run=False,
                    disable_batch=False, interruptible=True,
                    execution_settings=None):
        """
        Creates a task for this project.

        :param name: Task name.
        :param app: CWL app identifier.
        :param revision: CWL app revision.
        :param batch_input: Batch input.
        :param batch_by: Batch criteria.
        :param inputs: Input map.
        :param description: Task description.
        :param run: True if you want to run a task upon creation.
        :param disable_batch: True if you want to disable batching.
        :param interruptible: True if you want to use interruptible instances.
        :param execution_settings: Execution settings for the task.
        :return: Task object.
        """
        return self._api.tasks.create(
            name=name, project=self, app=app, revision=revision,
            batch_input=batch_input, batch_by=batch_by, inputs=inputs,
            description=description, run=run, disable_batch=disable_batch,
            interruptible=interruptible, execution_settings=execution_settings
        )
