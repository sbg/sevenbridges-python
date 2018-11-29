import logging

import six

from sevenbridges.errors import SbgError
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField, BooleanField,
    DictField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.bulk import BulkRecord
from sevenbridges.models.compound.error import Error
from sevenbridges.models.compound.volumes.properties import VolumeProperties
from sevenbridges.models.compound.volumes.volume_file import VolumeFile
from sevenbridges.models.file import File

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class Export(Resource):
    """
    Central resource for managing exports.
    """
    _URL = {
        'query': '/storage/exports',
        'get': '/storage/exports/{id}',

        'bulk_get': '/bulk/storage/exports/get',
        'bulk_create': '/bulk/storage/exports/create',
    }

    href = HrefField()
    id = StringField(read_only=True)
    state = StringField(read_only=True)
    _source = DictField(name='source', read_only=True)
    destination = CompoundField(VolumeFile, read_only=True)
    started_on = DateTimeField(read_only=True)
    finished_on = DateTimeField(read_only=True)
    overwrite = BooleanField(read_only=True)
    error = CompoundField(Error, read_only=True)
    _result = DictField(name='result', read_only=True)
    properties = CompoundField(VolumeProperties, read_only=True)

    def __str__(self):
        return six.text_type('<Export: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def source(self):
        try:
            return File(id=self._source['file'], api=self._api)
        except TypeError:
            return None

    @property
    def result(self):
        try:
            return File(api=self._api, **self._result)
        except TypeError:
            return None

    @classmethod
    def submit_export(cls, file, volume, location, properties=None,
                      overwrite=False, copy_only=False, api=None):

        """
        Submit new export job.
        :param file: File to be exported.
        :param volume: Volume identifier.
        :param location: Volume location.
        :param properties: Properties dictionary.
        :param overwrite: If true it will overwrite file if exists
        :param copy_only: If true files are kept on SevenBridges bucket.
        :param api: Api Instance.
        :return: Export object.
        """
        data = {}
        params = {}

        volume = Transform.to_volume(volume)
        file = Transform.to_file(file)
        destination = {
            'volume': volume,
            'location': location
        }
        source = {
            'file': file
        }
        if properties:
            data['properties'] = properties

        data['source'] = source
        data['destination'] = destination
        data['overwrite'] = overwrite

        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Submitting export', extra=extra)

        api = api if api else cls._API
        if copy_only:
            params['copy_only'] = True
            _export = api.post(
                cls._URL['query'], data=data, params=params).json()
        else:
            _export = api.post(
                cls._URL['query'], data=data).json()

        return Export(api=api, **_export)

    @classmethod
    def query(cls, volume=None, state=None, offset=None,
              limit=None, api=None):

        """
        Query (List) exports.
        :param volume: Optional volume identifier.
        :param state: Optional import sate.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API

        if volume:
            volume = Transform.to_volume(volume)

        return super(Export, cls)._query(
            url=cls._URL['query'], volume=volume, state=state, offset=offset,
            limit=limit, fields='_all', api=api
        )

    @classmethod
    def bulk_get(cls, exports, api=None):
        """
        Retrieve exports in bulk.
        :param exports: Exports to be retrieved.
        :param api: Api instance.
        :return: list of ExportBulkRecord objects.
        """
        api = api or cls._API
        export_ids = [Transform.to_export(export) for export in exports]
        data = {'export_ids': export_ids}

        response = api.post(url=cls._URL['bulk_get'], data=data)
        return ExportBulkRecord.parse_records(response=response, api=api)

    @classmethod
    def bulk_submit(cls, exports, copy_only=False, api=None):
        """
        Create exports in bulk.
        :param exports: Exports to be submitted in bulk.
        :param copy_only: If true files are kept on SevenBridges bucket.
        :param api: Api instance.
        :return: list of ExportBulkRecord objects.
        """
        if not exports:
            raise SbgError('Exports are required')

        api = api or cls._API

        items = []
        for export in exports:
            file_ = Transform.to_file(export.get('file'))
            volume = Transform.to_volume(export.get('volume'))
            location = Transform.to_location(export.get('location'))
            properties = export.get('properties', {})
            overwrite = export.get('overwrite', False)

            item = {
                'source': {
                    'file': file_
                },
                'destination': {
                    'volume': volume,
                    'location': location
                },
                'properties': properties,
                'overwrite': overwrite
            }

            items.append(item)

        data = {'items': items}
        params = {'copy_only': copy_only}

        response = api.post(
            url=cls._URL['bulk_create'], params=params, data=data
        )
        return ExportBulkRecord.parse_records(response=response, api=api)


class ExportBulkRecord(BulkRecord):
    resource = CompoundField(cls=Export)

    def __str__(self):
        return six.text_type('<ExportBulkRecord>')
