import logging

import six

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import ResourceNotModified
from sevenbridges.meta.collection import Collection, VolumeCollection
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField, BooleanField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.volumes.service import VolumeService
from sevenbridges.models.compound.volumes.volume_object import VolumeObject
from sevenbridges.models.compound.volumes.volume_prefix import VolumePrefix
from sevenbridges.models.enums import VolumeType
from sevenbridges.models.link import Link, VolumeLink
from sevenbridges.models.member import Member

logger = logging.getLogger(__name__)


# noinspection PyProtectedMember
class Volume(Resource):
    """
    Central resource for managing volumes.
    """
    _URL = {
        'query': '/storage/volumes',
        'get': '/storage/volumes/{id}',
        'delete': '/storage/volumes/{id}',
        'list': '/storage/volumes/{id}/list',
        'object': '/storage/volumes/{id}/object',
        'member': '/storage/volumes/{id}/members/{username}',
        'members_query': '/storage/volumes/{id}/members',
    }

    href = HrefField()
    id = StringField(read_only=True)
    name = StringField(read_only=False)
    description = StringField(read_only=False)
    access_mode = StringField(read_only=False)
    service = CompoundField(VolumeService, read_only=True)
    created_on = DateTimeField(read_only=True)
    modified_on = DateTimeField(read_only=True)
    active = BooleanField(read_only=True)

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type('<Volume: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, offset=None, limit=None, api=None):

        """
        Query (List) volumes.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API
        return super(Volume, cls)._query(
            url=cls._URL['query'], offset=offset, limit=limit,
            fields='_all', api=api
        )

    @classmethod
    def create_s3_volume(cls, name, bucket, access_key_id, secret_access_key,
                         access_mode, description=None, prefix=None,
                         properties=None, api=None):

        """
        Create s3 volume.
        :param name: Volume name.
        :param bucket: Referenced bucket.
        :param access_key_id: Amazon access key identifier.
        :param secret_access_key: Amazon secret access key.
        :param access_mode: Access Mode.
        :param description: Volume description.
        :param prefix: Volume prefix.
        :param properties: Volume properties.
        :param api: Api instance.
        :return: Volume object.
        """
        service = {'type': VolumeType.S3,
                   'bucket': bucket,
                   'credentials': {'access_key_id': access_key_id,
                                   'secret_access_key': secret_access_key
                                   }
                   }
        if prefix:
            service['prefix'] = prefix
        if properties:
            service['properties'] = properties

        data = {'name': name,
                'service': service,
                'access_mode': access_mode
                }
        if description:
            data['description'] = description
        api = api or cls._API
        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Creating s3 volume', extra=extra)
        response = api.post(url=cls._URL['query'], data=data).json()
        return Volume(api=api, **response)

    @classmethod
    def create_google_volume(cls, name, bucket, client_email, private_key,
                             access_mode, description=None, prefix=None,
                             properties=None, api=None):

        """
        Create s3 volume.
        :param name: Volume name.
        :param bucket: Referenced bucket.
        :param client_email: Google client email.
        :param private_key: Google client private key.
        :param access_mode: Access Mode.
        :param description: Volume description.
        :param prefix: Volume prefix.
        :param properties: Volume properties.
        :param api: Api instance.
        :return: Volume object.
        """
        service = {'type': VolumeType.GOOGLE,
                   'bucket': bucket,
                   'credentials': {'client_email': client_email,
                                   'private_key': private_key
                                   }
                   }
        if prefix:
            service['prefix'] = prefix
        if properties:
            service['properties'] = properties

        data = {'name': name,
                'service': service,
                'access_mode': access_mode
                }
        if description:
            data['description'] = description
        api = api or cls._API

        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Creating google volume', extra=extra)
        response = api.post(url=cls._URL['query'], data=data).json()
        return Volume(api=api, **response)

    @classmethod
    def create_oss_volume(cls, name, bucket, endpoint, access_key_id,
                          secret_access_key, access_mode, description=None,
                          prefix=None, properties=None, api=None):
        """
        Create oss volume.
        :param name: Volume name.
        :param bucket: Referenced bucket.
        :param access_key_id: Access key identifier.
        :param secret_access_key: Secret access key.
        :param access_mode: Access Mode.
        :param endpoint: Volume Endpoint.
        :param description: Volume description.
        :param prefix: Volume prefix.
        :param properties: Volume properties.
        :param api: Api instance.
        :return: Volume object.
        """
        service = {
            'type': VolumeType.OSS,
            'bucket': bucket,
            'endpoint': endpoint,
            'credentials': {
                'access_key_id': access_key_id,
                'secret_access_key': secret_access_key
            }
        }
        if prefix:
            service['prefix'] = prefix
        if properties:
            service['properties'] = properties

        data = {
            'name': name,
            'service': service,
            'access_mode': access_mode
        }
        if description:
            data['description'] = description
        api = api or cls._API
        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Creating oss volume', extra=extra)
        response = api.post(url=cls._URL['query'], data=data).json()
        return Volume(api=api, **response)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the volume on the server.
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
            logger.info('Saving volume', extra=extra)
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=modified_data).json()
            volume = Volume(api=self._api, **data)
            return volume
        else:
            raise ResourceNotModified()

    def list(self, prefix=None, limit=50):

        params = {
            'limit': limit
        }
        if prefix:
            params['prefix'] = prefix

        data = self._api.get(
            url=self._URL['list'].format(id=self.id), params=params).json()

        href = data['href']
        links = [VolumeLink(**link) for link in data['links']]

        objects = [
            VolumeObject(api=self._api, **item) for item in data['items']
            # noqa: F812
        ]
        prefixes = [
            VolumePrefix(api=self._api, **prefix) for prefix in  # noqa: F812
            data['prefixes']
        ]
        return VolumeCollection(
            href=href, items=objects, links=links,
            prefixes=prefixes, api=self._api
        )

    def get_volume_object_info(self, location):
        """
        Fetches information about single volume object - usually file
        :param location: object location
        :return:
        """
        param = {'location': location}
        data = self._api.get(url=self._URL['object'].format(
            id=self.id), params=param).json()
        return VolumeObject(api=self._api, **data)

    def get_imports(self, project=None, state=None, offset=None, limit=None):
        """
        Fetches imports for this volume.
        :param project: Optional project identifier.
        :param state: Optional state.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        return self._api.imports.query(volume=self, project=project,
                                       state=state, offset=offset, limit=limit)

    def get_exports(self, state=None, offset=None, limit=None):
        """
        Fetches exports for this volume.
        :param state: Optional state.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        return self._api.exports.query(volume=self, state=state, offset=offset,
                                       limit=limit
                                       )

    def get_members(self, offset=None, limit=None):
        """
        Retrieves volume members.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        extra = {
            'resource': self.__class__.__name__,
            'query': {'id': self.id}
        }
        logger.info('Get volume members', extra=extra)
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
        Add a member to the volume.
        :param user:  Member username
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        user = Transform.to_user(user)
        data = {'id': user, 'type': 'USER'}

        if 'execute' in permissions:
            permissions.pop('execute')

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
        logger.info('Adding volume member using username', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def add_member_team(self, team, permissions):
        """
        Add a member (team) to a volume.
        :param team: Team object or team identifier.
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        team = Transform.to_team(team)
        data = {'id': team, 'type': 'TEAM'}

        if 'execute' in permissions:
            permissions.pop('execute')

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
        logger.info('Adding volume team member using team id', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def add_member_division(self, division, permissions):
        """
        Add a member (team) to a volume.
        :param division: Division object or division identifier.
        :param permissions: Permissions dictionary.
        :return: Member object.
        """
        division = Transform.to_division(division)

        if 'execute' in permissions:
            permissions.pop('execute')

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
        logger.info('Adding volume team member using division id', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return Member(api=self._api, **member_data)

    def get_member(self, username, api=None):
        """
        Fetches information about a single volume member
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
        Remove member from the volume.
        :param user: User to be removed.
        """
        member = Transform.to_user(user)
        extra = {
            'resource': self.__class__.__name__,
            'query': {
                'id': self.id,
                'user': user,
            }
        }
        logger.info('Removing volume member', extra=extra)
        self._api.delete(
            url=self._URL['member'].format(id=self.id, member=member)
        )
