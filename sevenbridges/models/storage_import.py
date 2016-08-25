import six

from sevenbridges.meta.resource import Resource
from sevenbridges.models.file import File
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.error import Error
from sevenbridges.models.compound.volumes.volume_file import VolumeFile
from sevenbridges.models.compound.volumes.import_destination import (
    ImportDestination
)
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField, BooleanField,
    DictField
)


# noinspection PyArgumentList
class Import(Resource):
    """
    Central resource for managing imports.
    """
    _URL = {
        'query': '/storage/imports',
        'get': '/storage/imports/{id}',
    }

    href = HrefField()
    id = StringField(read_only=True)
    state = StringField(read_only=True)
    source = CompoundField(VolumeFile, read_only=True)
    destination = CompoundField(ImportDestination, read_only=True)
    started_on = DateTimeField(read_only=True)
    finished_on = DateTimeField(read_only=True)
    overwrite = BooleanField(read_only=True)
    error = CompoundField(Error, read_only=True)
    _result = DictField(name='result', read_only=True)

    def __str__(self):
        return six.text_type('<Import: id={id}>'.format(id=self.id))

    @property
    def result(self):
        try:
            return File(id=self._result['id'], api=self._api)
        except TypeError:
            return None

    @classmethod
    def submit_import(cls, volume, location, project, name=None,
                      overwrite=False, properties=None, api=None):

        """
        Submits new import job.
        :param volume: Volume identifier.
        :param location: Volume location.
        :param project: Project identifier.
        :param name: Optional file name.
        :param overwrite: If true it will overwrite file if exists.
        :param properties: Properties dictionary.
        :param api: Api instance.
        :return: Import object.
        """
        data = {}
        volume = Transform.to_volume(volume)
        project = Transform.to_project(project)
        source = {
            'volume': volume,
            'location': location
        }
        destination = {
            'project': project
        }
        if name:
            destination['name'] = name

        data['source'] = source
        data['destination'] = destination
        data['overwrite'] = overwrite

        if properties:
            data['properties'] = properties

        api = api if api else cls._API
        _import = api.post(cls._URL['query'], data=data).json()
        return Import(api=api, **_import)

    @classmethod
    def query(cls, project=None, volume=None, state=None, offset=None,
              limit=None, api=None):

        """
        Query (List) imports.
        :param project: Optional project identifier.
        :param volume: Optional volume identifier.
        :param state: Optional import sate.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API

        if project:
            project = Transform.to_project(project)
        if volume:
            volume = Transform.to_volume(volume)

        return super(Import, cls)._query(
            url=cls._URL['query'], project=project, volume=volume, state=state,
            fields='_all', offset=offset, limit=limit, api=api
        )
