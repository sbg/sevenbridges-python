import logging

import six

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import ResourceNotModified
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.markers.position import MarkerPosition

logger = logging.getLogger(__name__)


class Marker(Resource):
    _URL = {
        'query': '/genome/markers',
        'get': '/genome/markers/{id}',
        'delete': '/genome/markers/{id}'
    }

    href = HrefField()
    id = StringField(read_only=True)
    file = StringField(read_only=True)
    name = StringField(read_only=False)
    chromosome = StringField(read_only=False)
    position = CompoundField(MarkerPosition, read_only=False)
    created_time = DateTimeField()
    created_by = StringField(read_only=True)

    def __str__(self):
        return six.text_type('<Marker: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def query(cls, file, offset=None, limit=None, api=None):
        """
        Queries genome markers on a file.
        :param file: Genome file - Usually bam file.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api if api else cls._API

        file = Transform.to_file(file)
        return super(Marker, cls)._query(
            url=cls._URL['query'], offset=offset, limit=limit,
            file=file, fields='_all', api=api
        )

    @classmethod
    def create(cls, file, name, position, chromosome, private=True, api=None):
        """
        Create a marker on a file.
        :param file: File object or identifier.
        :param name: Marker name.
        :param position: Marker position object.
        :param chromosome: Chromosome number.
        :param private: Whether the marker is private or public.
        :param api: Api instance.
        :return: Marker object.
        """
        api = api if api else cls._API

        file = Transform.to_file(file)
        data = {
            'file': file,
            'name': name,
            'position': position,
            'chromosome': chromosome,
            'private': private
        }

        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Creating marker', extra=extra)
        marker_data = api.post(url=cls._URL['query'], data=data).json()
        return Marker(api=api, **marker_data)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the marker on the server.
        :param inplace Apply edits on the current instance or get a new one.
        :return: Marker instance.
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
            logger.info('Saving marker', extra=extra)
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=modified_data).json()
            marker = Marker(api=self._api, **data)
            return marker
        else:
            raise ResourceNotModified()

    def delete(self):
        super(Marker, self).delete()

    def reload(self):
        super(Marker, self).reload()
