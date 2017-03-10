import six

from sevenbridges.errors import ResourceNotModified
from sevenbridges.meta.resource import Resource
from sevenbridges.decorators import inplace_reload
from sevenbridges.models.compound.volumes.service import VolumeService
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField, BooleanField
)
from sevenbridges.models.enums import VolumeType


# noinspection PyProtectedMember
class Volume(Resource):
    """
    Central resource for managing volumes.
    """
    _URL = {
        'query': '/storage/volumes',
        'get': '/storage/volumes/{id}',
        'delete': '/storage/volumes/{id}',
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
            url=cls._URL['query'], offset=offset, limit=limit, fields='_all',
            api=api
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
        response = api.post(url=cls._URL['query'], data=data).json()
        return Volume(api=api, **response)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the volume on the server.
        """
        modified_data = self._modified_data()
        if bool(modified_data):
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=modified_data).json()
            volume = Volume(api=self._api, **data)
            return volume
        else:
            raise ResourceNotModified()

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
