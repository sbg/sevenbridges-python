import six

from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.volumes.properties import VolumeProperties
from sevenbridges.models.file import File
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.error import Error
from sevenbridges.models.compound.volumes.volume_file import VolumeFile
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField, BooleanField,
    DictField
)


# noinspection PyArgumentList
class Export(Resource):
    """
    Central resource for managing exports.
    """
    _URL = {
        'query': '/storage/exports',
        'get': '/storage/exports/{id}',
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

    @property
    def source(self):
        try:
            return File(id=self._source['file'], api=self._api)
        except TypeError:
            return None

    @property
    def result(self):
        try:
            return File(id=self._result['id'], api=self._api)
        except TypeError:
            return None

    @classmethod
    def submit_export(cls, file, volume, location, properties=None,
                      overwrite=False, api=None):

        """
        Submit new export job.
        :param file: File to be exported.
        :param volume: Volume identifier.
        :param location: Volume location.
        :param properties: Properties dictionary.
        :param overwrite: If true it will overwrite file if exists
        :param api: Api Instance.
        :return: Export object.
        """
        data = {}
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

        api = api if api else cls._API
        _export = api.post(cls._URL['query'], data=data).json()
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
