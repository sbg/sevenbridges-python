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
from sevenbridges.models.compound.volumes.import_destination import (
    ImportDestination
)
from sevenbridges.models.compound.volumes.volume_file import VolumeFile
from sevenbridges.models.file import File

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class Import(Resource):
    """
    Central resource for managing imports.
    """
    _URL = {
        'query': '/storage/imports',
        'get': '/storage/imports/{id}',

        'bulk_get': '/bulk/storage/imports/get',
        'bulk_create': '/bulk/storage/imports/create',
    }

    href = HrefField()
    id = StringField(read_only=True)
    state = StringField(read_only=True)
    preserve_folder_structure = BooleanField(read_only=True)
    source = CompoundField(VolumeFile, read_only=True)
    destination = CompoundField(ImportDestination, read_only=True)
    started_on = DateTimeField(read_only=True)
    finished_on = DateTimeField(read_only=True)
    overwrite = BooleanField(read_only=True)
    error = CompoundField(Error, read_only=True)
    _result = DictField(name='result', read_only=True)

    def __str__(self):
        return six.text_type('<Import: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def result(self):
        try:
            return File(api=self._api, **self._result)
        except TypeError:
            return None

    @classmethod
    def submit_import(cls, volume, location, project=None, name=None,
                      overwrite=False, properties=None, parent=None,
                      preserve_folder_structure=True, api=None):
        """
        Submits new import job.
        :param volume: Volume identifier.
        :param location: Volume location.
        :param project: Project identifier.
        :param name: Optional file name.
        :param overwrite: If true it will overwrite file if exists.
        :param properties: Properties dictionary.
        :param parent: The ID of the target folder to which the item should be
            imported. Should not be used together with project.
        :param preserve_folder_structure: Whether to keep the exact source
            folder structure. The default value is true if the item being
            imported is a folder. Should not be used if you are importing
            a file.
        :param api: Api instance.
        :return: Import object.
        """
        data = {}
        volume = Transform.to_volume(volume)

        if project and parent:
            raise SbgError(
                'Project and parent identifiers are mutually exclusive'
            )
        elif project:
            project = Transform.to_project(project)
            destination = {
                'project': project
            }
        elif parent:
            parent = Transform.to_file(parent)
            destination = {
                'parent': parent
            }
        else:
            raise SbgError('Project or parent identifier is required.')

        source = {
            'volume': volume,
            'location': location
        }

        if name:
            destination['name'] = name

        data['source'] = source
        data['destination'] = destination
        data['overwrite'] = overwrite

        if not preserve_folder_structure:
            data['preserve_folder_structure'] = preserve_folder_structure

        if properties:
            data['properties'] = properties

        api = api if api else cls._API
        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Submitting import', extra=extra)
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
        :param offset: Pagination offset.
        :param limit: Pagination limit.
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

    @classmethod
    def bulk_get(cls, imports, api=None):
        """
        Retrieve imports in bulk
        :param imports: Imports to be retrieved.
        :param api: Api instance.
        :return: List of ImportBulkRecord objects.
        """
        api = api or cls._API
        import_ids = [Transform.to_import(import_) for import_ in imports]
        data = {'import_ids': import_ids}

        response = api.post(url=cls._URL['bulk_get'], data=data)
        return ImportBulkRecord.parse_records(response=response, api=api)

    @classmethod
    def bulk_submit(cls, imports, api=None):
        """
        Submit imports in bulk
        :param imports: Imports to be retrieved.
        :param api: Api instance.
        :return: List of ImportBulkRecord objects.
        """
        if not imports:
            raise SbgError('Imports are required')

        api = api or cls._API

        items = []
        for import_ in imports:
            volume = Transform.to_volume(import_.get('volume'))
            location = Transform.to_location(import_.get('location'))
            project = Transform.to_project(import_.get('project'))
            name = import_.get('name', None)
            overwrite = import_.get('overwrite', False)

            item = {
                'source': {
                    'volume': volume,
                    'location': location
                },
                'destination': {
                    'project': project
                },
                'overwrite': overwrite
            }

            if name:
                item['destination']['name'] = name

            items.append(item)

        data = {'items': items}

        response = api.post(url=cls._URL['bulk_create'], data=data)
        return ImportBulkRecord.parse_records(response=response, api=api)


class ImportBulkRecord(BulkRecord):
    resource = CompoundField(cls=Import)

    def __str__(self):
        return six.text_type('<ImportBulkRecord>')
