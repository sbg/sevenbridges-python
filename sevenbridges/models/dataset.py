import six
import logging

from sevenbridges.models.link import Link
from sevenbridges.models.member import Member
from sevenbridges.decorators import inplace_reload
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.collection import Collection
from sevenbridges.meta.transformer import Transform
from sevenbridges.meta.fields import HrefField, StringField


logger = logging.getLogger(__name__)


class Dataset(Resource):
    """Central resource for managing datasets."""

    _URL = {
        'query': '/datasets',
        'owned_by': '/datasets/{username}',
        'get': '/datasets/{id}',
        'delete': '/datasets/{id}',
        'members': '/datasets/{id}/members',
        'member': '/datasets/{id}/members/{username}',
        'permissions': '/datasets/{id}/members/{username}/permissions',
    }

    href = HrefField()
    id = StringField(read_only=True)
    name = StringField()
    description = StringField()

    def __str__(self):
        return six.text_type('<Dataset: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def query(cls, visibility=None, api=None):
        """Query ( List ) datasets
        :param visibility: If provided as 'public', retrieves public datasets
        :param api: Api instance
        :return: Collection object
        """
        api = api if api else cls._API

        return super(Dataset, cls)._query(
            url=cls._URL['query'],
            visibility=visibility,
            fields='_all', api=api
        )

    @classmethod
    def get_owned_by(cls, username, api=None):
        """Query ( List ) datasets by owner
        :param api: Api instance
        :param username: Owner username
        :return: Collection object
        """
        api = api if api else cls._API

        return super(Dataset, cls)._query(
            url=cls._URL['owned_by'].format(username=username),
            fields='_all',
            api=api
        )

    @inplace_reload
    def save(self, inplace=True):
        """Save all modification to the dataset on the server.
        :param inplace: Apply edits on the current instance or get a new one.
        :return: Dataset instance.
        """
        modified_data = self._modified_data()
        if bool(modified_data):
            dataset_request_data = {}

            name = modified_data.pop('name', None)
            description = modified_data.pop('description', None)
            dataset_request_data.update(modified_data)

            if name:
                dataset_request_data['name'] = name

            if description:
                dataset_request_data['description'] = description

            response = self._api.patch(
                url=self._URL['get'].format(id=self.id),
                data=dataset_request_data
            )
            data = response.json()

            dataset = Dataset(api=self._api, **data)
            return dataset

    def get_members(self, api=None):
        """Retrieve dataset members
        :param api: Api instance
        :return: Collection object
        """
        api = api or self._API

        response = api.get(url=self._URL['members'].format(id=self.id))

        data = response.json()
        total = response.headers['x-total-matching-query']
        members = [Member(api=api, **member) for member in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']

        return Collection(
            resource=Member,
            href=href,
            total=total,
            items=members,
            links=links,
            api=api
        )

    def get_member(self, username, api=None):
        """Retrieve dataset member
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

    def add_member(self, username, permissions, api=None):
        """Add member to a dataset
        :param username: Member username
        :param permissions: Permissions dict
        :param api: Api instance
        :return: New member instance
        """
        api = api or self._API
        data = {
            'username': username,
            'permissions': permissions
        }

        response = api.post(
            url=self._URL['members'].format(id=self.id),
            data=data
        )
        data = response.json()
        return Member(api=api, **data)

    def remove_member(self, member, api=None):
        """Remove member from a dataset
        :param member: Member username
        :param api: Api instance
        :return: None
        """
        api = api or self._API
        username = Transform.to_member(member)

        api.delete(
            url=self._URL['member'].format(
                id=self.id,
                username=username
            )
        )
