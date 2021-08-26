import logging

from sevenbridges.errors import SbgError
from sevenbridges.meta.fields import (
    HrefField, StringField, CompoundField, DateTimeField,
    DictField, IntegerField
)
from sevenbridges.models.bulk import BulkRecord
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.file import File

logger = logging.getLogger(__name__)


class DRSImport(Resource):
    """
    Central resource for managing DRS imports.
    """
    _URL = {
        'bulk_get': '/bulk/drs/imports/get',
        'bulk_create': '/bulk/drs/imports/create',
    }

    id = StringField(read_only=True)
    href = HrefField(read_only=True)
    result = DictField(read_only=True)
    failed_files = IntegerField(read_only=True)
    completed_files = IntegerField(read_only=True)
    total_files = IntegerField(read_only=True)
    state = StringField(read_only=True)
    started_on = DateTimeField(read_only=True)
    finished_on = DateTimeField(read_only=True)

    def __str__(self):
        return f'<Import: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    @property
    def result_files(self):
        try:
            return [File(api=self._api, **file) for file in self.result]
        except TypeError:
            return None

    @classmethod
    def bulk_get(cls, import_job_id, api=None):
        """
        Retrieve imports in bulk
        :param import_job_id: Import id to be retrieved.
        :param api: Api instance.
        :return: List of response_obj objects.
        """
        api = api or cls._API
        import_id = Transform.to_import(import_job_id)

        response = api.post(url=cls._URL['bulk_get'], data={'id': import_id})
        return DRSImportBulkResponse.parse_records(response=response, api=api)

    @classmethod
    def bulk_submit(cls, imports, tags, conflict_resolution='SKIP', api=None):
        """
        Submit DRS bulk import
        :param imports:  List of dicts describing a wanted import.
        :param tags: list of tags to be applied
        :param conflict_resolution:
        :param api: Api instance.
        :return: List of DRSImportBulkRecord objects.
        """
        imports = [{
            "drs_uri": "drs://caninedc.org/01349ad3-6008-426f-a17c-88dcc00492fe",
            "parent": "568cf5dce4b0307bc0462060",
            "project": "john-doe/project-slug",
            "metadata": {"study_id": "123", "cohort": 2}
        }]
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
        response = api.post(url=cls._URL['bulk_create'], data=data)

        return DRSImportBulkResponse.parse_records(response=response, api=api)

    def reload(self):
        response = self.api.post(
            url=self._URL['bulk_get'], data={'id': self.id}
        )
        return DRSImportBulkResponse.parse_records(
            response=response, api=self.api
        )


class DRSImportBulkResponse(BulkRecord):
    resource = CompoundField(cls=DRSImport, read_only=False)

    def __str__(self):
        return f'<DRSImportBulkRecord valid={self.valid}>'
