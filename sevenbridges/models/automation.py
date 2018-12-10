import logging

import six

from sevenbridges.models.file import File
from sevenbridges.meta.transformer import Transform
from sevenbridges.meta.resource import Resource
from sevenbridges.decorators import inplace_reload
from sevenbridges.models.member import Permissions
from sevenbridges.errors import ResourceNotModified
from sevenbridges.models.enums import AutomationRunActions
from sevenbridges.meta.fields import (
    DictField,
    HrefField,
    StringField,
    CompoundField,
    DateTimeField,
)


logger = logging.getLogger(__name__)


class AutomationPackage(Resource):
    """
    Central resource for managing automation packages.
    """
    _URL = {
        'query': '/automation/automations/{automation_id}/packages',
    }

    id = StringField(read_only=True)
    automation = StringField(read_only=True)
    version = StringField(read_only=True)
    location = StringField(read_only=True)
    created_by = StringField(read_only=True)
    created_on = StringField(read_only=True)

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type('<AutomationPackage: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, automation=None, offset=None, limit=None, api=None):
        """
        Query (List) automation packages.
        :param automation: Automation id.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: collection object
        """
        automation_id = Transform.to_automation(automation)

        api = api or cls._API
        return super(AutomationPackage, cls)._query(
            url=cls._URL['query'].format(automation_id=automation_id),
            automation_id=automation_id,
            offset=offset,
            limit=limit,
            api=api,
        )


class AutomationMember(Resource):
    """
    Central resource for managing automation members.
    """
    _URL = {
        'query': '/automation/automations/{automation_id}/members',
        'get': '/automation/automations/{automation_id}/members/{id}',
    }

    href = HrefField()
    username = StringField(read_only=True)
    permissions = CompoundField(Permissions)

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.username == other.username

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type(
            '<AutomationMember: username={username}>'
            .format(username=self.username)
        )

    @classmethod
    def query(cls, automation=None, offset=None, limit=None, api=None):
        """
        Query (List) apps.
        :param automation: Automation id.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: collection object
        """
        automation_id = Transform.to_automation(automation)

        api = api or cls._API
        return super(AutomationMember, cls)._query(
            url=cls._URL['query'].format(automation_id=automation_id),
            automation_id=automation_id,
            offset=offset,
            limit=limit,
            api=api,
        )

    # noinspection PyMethodOverriding
    @classmethod
    def get(cls, id, automation, api=None):
        """
        Fetches the resource from the server.
        :param id: Automation member username
        :param automation: Automation id or object
        :param api: sevenbridges Api instance.
        :return: AutomationMember object.
        """
        username = Transform.to_resource(id)
        automation = Transform.to_automation(automation)

        api = api or cls._API
        member = api.get(url=cls._URL['get'].format(
            automation_id=automation,
            id=username
        )).json()
        return AutomationMember(api=api, **member)

    @classmethod
    def add(cls, user, permissions, automation, api=None):
        """
        Add a member to the automation.
        :param user: Member username
        :param permissions: Permissions dictionary.
        :param automation: Automation object or id
        :param api: sevenbridges Api instance
        :return: Automation member object.
        """
        user = Transform.to_user(user)
        automation = Transform.to_automation(automation)

        api = api or cls._API
        data = {'username': user}

        if isinstance(permissions, dict):
            data.update({
                'permissions': permissions
            })

        member_data = api.post(
            url=cls._URL['query'].format(automation_id=automation),
            data=data
        ).json()
        return AutomationMember(api=api, **member_data)

    @classmethod
    def remove(cls, user, automation, api=None):
        """
        Remove a member from the automation.
        :param user: Member username
        :param automation: Automation id
        :param api: sevenbridges Api instance
        :return: None
        """
        user = Transform.to_user(user)
        automation = Transform.to_automation(automation)

        api = api or cls._API
        api.delete(
            cls._URL['get'].format(automation_id=automation, id=user)
        )

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves modification to the api server.
        """
        modified = self._modified_data()
        if bool(modified):
            new_data = self.permissions.copy()
            new_data.update(modified['permissions'])
            data = {
                'permissions': new_data
            }
            url = six.text_type(self.href)
            self._api.patch(url=url, data=data, append_base=False)
        else:
            raise ResourceNotModified()


class Automation(Resource):
    """
    Central resource for managing automations.
    """
    _URL = {
        'query': '/automation/automations',
        'get': '/automation/automations/{id}',
        'member': AutomationMember._URL['get'],
        'members': AutomationMember._URL['query'],
        'packages': AutomationPackage._URL['query'],
    }

    href = HrefField()
    id = StringField(read_only=True)
    name = StringField(read_only=True)
    description = StringField(read_only=True)
    owner = StringField(read_only=True)
    created_by = StringField(read_only=True)
    created_on = StringField(read_only=True)
    modified_by = StringField(read_only=True)
    modified_on = StringField(read_only=True)

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type(
            '<Automation: id={id} name={name}>'
            .format(id=self.id, name=self.name)
        )

    @classmethod
    def query(cls, name=None, offset=None, limit=None, api=None):
        """
        Query (List) automations.
        :param name: Automation name.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: collection object
        """

        api = api or cls._API
        return super(Automation, cls)._query(
            url=cls._URL['query'],
            name=name,
            offset=offset,
            limit=limit,
            api=api,
        )

    def get_packages(self, offset=None, limit=None, api=None):
        """
        Return list of packages that belong to this automation
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: sevenbridges Api instance.
        :return: AutomationPackage collection
        """
        api = api or self._API
        return AutomationPackage.query(
            automation=self.id, offset=offset, limit=limit, api=api
        )

    def get_member(self, username, api=None):
        """
        Return specified automation member
        :param username: Member username
        :param api: sevenbridges Api instance.
        :return: AutomationMember object
        """
        member = Transform.to_automation_member(username)
        api = api or self._API
        return AutomationMember.get(
            id=member, automation=self.id, api=api
        )

    def get_members(self, offset=None, limit=None, api=None):
        """
        Return list of automation members
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: sevenbridges Api instance.
        :return: AutomationMember collection
        """
        api = api or self._API
        return AutomationMember.query(
            automation=self.id, offset=offset, limit=limit, api=api
        )

    def add_member(self, user, permissions, api=None):
        """
        Add member to the automation
        :param user: Member username
        :param permissions: Member permissions
        :param api: sevenbridges Api instance
        :return: AutomationMember object
        """
        api = api or self._API
        return AutomationMember.add(
            automation=self.id, user=user, permissions=permissions, api=api
        )

    def remove_member(self, user, api=None):
        """
        Remove a member from the automation
        :param user: Member username
        :param api: sevenbridges Api instance
        :return: None
        """
        api = api or self._API
        AutomationMember.remove(automation=self.id, user=user, api=api)

    def get_runs(self, package=None, status=None, name=None,
                 created_by=None, created_from=None, created_to=None,
                 order_by=None, order=None, offset=None, limit=None, api=None):
        """
        Query automation runs that belong to this automation
        :param package: Package id
        :param status: Run status
        :param name: Automation run name
        :param created_by: Username of member that created the run
        :param created_from: Date the run was created after
        :param created_to: Date the run was created before
        :param order_by: Property by which to order results
        :param order: Ascending or Descending ("asc" or "desc")
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: sevenbridges Api instance
        :return: AutomationRun collection
        """
        api = api or self._API
        return AutomationRun.query(
            automation=self.id, package=package, status=status, name=name,
            created_by=created_by, created_from=created_from,
            created_to=created_to, order_by=order_by, order=order,
            offset=offset, limit=limit, api=api
        )


class AutomationRun(Resource):
    """
    Central resource for managing automation runs.
    """

    _URL = {
        'query': '/automation/runs',
        'get': '/automation/runs/{id}',
        'actions': '/automation/runs/{id}/actions/{action}',
        'state': '/automation/runs/{id}/state',
    }

    href = HrefField()
    id = StringField(read_only=True)
    name = StringField(read_only=True)
    automation = CompoundField(Automation, read_only=True)
    package = CompoundField(AutomationPackage, read_only=True)
    inputs = DictField()
    settings = DictField()
    created_on = DateTimeField(read_only=True)
    start_time = DateTimeField(read_only=True)
    end_time = DateTimeField(read_only=True)
    resumed_from = StringField(read_only=True)
    created_by = StringField(read_only=True)
    status = StringField(read_only=True)
    message = StringField(read_only=True)
    execution_details = DictField(read_only=True)

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type('<AutomationRun: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, automation=None, package=None, status=None, name=None,
              created_by=None, created_from=None, created_to=None,
              order_by=None, order=None, offset=None, limit=None, api=None):
        """
        Query (List) automation runs.
        :param name: Automation run name
        :param automation: Automation template
        :param package: Package
        :param status: Run status
        :param created_by: Username of user that created the run
        :param order_by: Property by which to order results
        :param order: Ascending or descending ("asc" or "desc")
        :param created_from: Date the run is created after
        :param created_to: Date the run is created before
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: collection object
        """
        if automation:
            automation = Transform.to_automation(automation)

        if package:
            package = Transform.to_automation_package(package)

        api = api or cls._API
        return super(AutomationRun, cls)._query(
            url=cls._URL['query'],
            name=name,
            automation=automation,
            package=package,
            status=status,
            created_by=created_by,
            created_from=created_from,
            created_to=created_to,
            order_by=order_by,
            order=order,
            offset=offset,
            limit=limit,
            api=api,
        )

    @classmethod
    def create(cls, package, inputs=None, settings=None, resume_from=None,
               name=None, secret_settings=None, api=None):
        """
        Create and start a new run.
        :param package: Automation package id
        :param inputs: Input dictionary
        :param settings: Settings override dictionary
        :param resume_from: Run to resume from
        :param name: Automation run name
        :param secret_settings: dict to override secret_settings from
        automation template
        :param api: sevenbridges Api instance
        :return: AutomationRun object
        """
        package = Transform.to_automation_package(package)

        data = {'package': package}
        if inputs:
            data['inputs'] = inputs
        if settings:
            data['settings'] = settings
        if resume_from:
            data['resume_from'] = resume_from
        if name:
            data['name'] = name
        if secret_settings:
            data['secret_settings'] = secret_settings

        api = api or cls._API
        automation_run = api.post(
            url=cls._URL['query'],
            data=data,
        ).json()
        return AutomationRun(api=api, **automation_run)

    def stop(self, api=None):
        """
        Stop automation run.
        :param api: sevenbridges Api instance.
        :return: AutomationRun object
        """
        api = api or self._API

        return api.post(
            url=self._URL['actions'].format(
                id=self.id, action=AutomationRunActions.STOP
            )
        ).content

    def get_log_file(self, api=None):
        """
        Retrieve automation run log.
        :param api: sevenbridges Api instance
        :return: Log string
        """
        api = api or self._API
        log_file_data = self.execution_details.get('log_file')
        return File(api=api, **log_file_data) if log_file_data else None

    def get_state(self, api=None):
        """
        Retrieve automation run state.
        :param api: sevenbridges Api instance
        :return: State file json contents as string
        """
        api = api or self._API
        return api.get(self._URL['state'].format(id=self.id)).json()
