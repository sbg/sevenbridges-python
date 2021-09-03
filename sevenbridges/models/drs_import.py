import logging

from sevenbridges.errors import SbgError
from sevenbridges.meta.fields import (
    HrefField, StringField, DateTimeField, CompoundListField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.import_result import FileImportResult
from sevenbridges.models.file import File

logger = logging.getLogger(__name__)


class DRSImportBulk(Resource):
    """
    Central resource for managing DRS imports.
    """
    _URL = {
        'get': '/bulk/drs/imports/{id}',
        'create': '/bulk/drs/imports/create',
    }

    id = StringField(read_only=True)
    href = HrefField(read_only=True)
    result = CompoundListField(FileImportResult, read_only=True)
    _result_files = []  # cache for result_files property
    state = StringField(read_only=True)
    started_on = DateTimeField(read_only=True)
    finished_on = DateTimeField(read_only=True)

    def __str__(self):
        return f'<DRSBulkImport: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    @property
    def result_files(self):
        """
        Retrieve files that were successfully imported.
        :return: List of File objects
        """
        try:
            cached_file_ids = set([
                file.resource.id for file in self._result_files
            ])

            imported_file_ids = set([
                file.resource.id
                for file in self.result if file.resource
            ])
            file_ids_to_retrieve = imported_file_ids - cached_file_ids
            if file_ids_to_retrieve:
                files = File.bulk_get(
                    files=file_ids_to_retrieve, api=self._api
                )
                self._result_files.extend(files)
            return self._result_files if self._result_files else None
        except TypeError:
            return None

    @classmethod
    def bulk_get(cls, import_job_id, api=None):
        """
        Retrieve DRS bulk import details
        :param import_job_id: Import id to be retrieved.
        :param api: Api instance.
        :return: DRSImportBulk object.
        """
        api = api or cls._API

        if not import_job_id:
            raise SbgError('DRS import is required!')
        elif not isinstance(import_job_id, str):
            raise SbgError('Invalid DRS import parameter!')

        response = api.get(
            url=cls._URL['get'].format(id=import_job_id)
        ).json()
        return DRSImportBulk(api=api, **response)

    @classmethod
    def bulk_submit(
            cls, imports, tags=None, conflict_resolution='SKIP', api=None
    ):
        """
        Submit DRS bulk import
        :param imports:  List of dicts describing a wanted import.
        :param tags: list of tags to be applied.
        :param conflict_resolution: Type of file naming conflict resolution.
        :param api: Api instance.
        :return: DRSImportBulk object.
        """
        if not imports:
            raise SbgError('Imports are required')

        api = api or cls._API

        items = []
        for import_ in imports:
            project = import_.get('project')
            parent = import_.get('parent')

            if project and parent:
                raise SbgError(
                    'Project and parent identifiers are mutually exclusive'
                )
            elif project:
                import_['project'] = Transform.to_project(project)
            elif parent:
                import_['parent'] = Transform.to_file(parent)
            else:
                raise SbgError('Project or parent identifier is required.')

            items.append(import_)

        data = {
            'conflict_resolution': conflict_resolution,
            'tags': tags,
            'items': items
        }
        response = api.post(url=cls._URL['create'], data=data).json()
        return DRSImportBulk(api=api, **response)
