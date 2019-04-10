import logging

import six

from sevenbridges.meta.resource import Resource
from sevenbridges.models.file import FileBulkRecord
from sevenbridges.meta.transformer import Transform
from sevenbridges.meta.fields import (
    BasicListField, DateTimeField, IntegerField, StringField,
)

logger = logging.getLogger(__name__)


class AsyncFileBulkRecord(FileBulkRecord):

    @classmethod
    def parse_records(cls, result, api=None):
        api = api or cls._API

        records = []
        for item in result:
            record = cls(api=api)
            if 'error' in item:
                record.error = item['error']
            if 'resource' in item:
                record.resource = item['resource']
            records.append(record)
        return records


class AsyncJob(Resource):
    """
    Central resource for managing async jobs
    """

    _URL = {
        'list_file_jobs': '/async/files',
        'get_file_copy_job': '/async/files/copy/{id}',
        'get_file_delete_job': '/async/files/delete/{id}',
        'bulk_copy_files': '/async/files/copy',
        'bulk_delete_files': '/async/files/delete'
    }

    id = StringField(read_only=True)
    type = StringField(read_only=True)
    state = StringField(read_only=True)
    result = BasicListField(read_only=True)
    total_files = IntegerField(read_only=True)
    failed_files = IntegerField(read_only=True)
    completed_files = IntegerField(read_only=True)
    started_on = DateTimeField(read_only=True)
    finished_on = DateTimeField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<AsyncJob: type={type} id={id}>'
            .format(id=self.id, type=self.type)
        )

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def get_file_copy_job(cls, id, api=None):
        """
        Retrieve file copy async job
        :param id: Async job identifier
        :param api: Api instance
        :return:
        """
        id = Transform.to_async_job(id)

        api = api if api else cls._API
        async_job = api.get(
            url=cls._URL['get_file_copy_job'].format(id=id)
        ).json()
        return AsyncJob(api=api, **async_job)

    @classmethod
    def get_file_delete_job(cls, id, api=None):
        """
        :param id: Async job identifier
        :param api: Api instance
        :return:
        """
        id = Transform.to_async_job(id)

        api = api if api else cls._API
        async_job = api.get(
            url=cls._URL['get_file_delete_job'].format(id=id)
        ).json()
        return AsyncJob(api=api, **async_job)

    def get_result(self, api=None):
        """
        Get async job result in bulk format
        :return: List of AsyncFileBulkRecord objects
        """
        api = api or self._API
        if not self.result:
            return []
        return AsyncFileBulkRecord.parse_records(
            result=self.result,
            api=api
        )

    @classmethod
    def list_file_jobs(cls, offset=None, limit=None, api=None):
        """Query ( List ) async jobs
        :param offset: Pagination offset
        :param limit: Pagination limit
        :param api: Api instance
        :return: Collection object
        """
        api = api or cls._API
        return super(AsyncJob, cls)._query(
            api=api,
            url=cls._URL['list_file_jobs'],
            offset=offset,
            limit=limit,
        )

    @classmethod
    def file_bulk_copy(cls, files, api=None):
        api = api or cls._API
        data = {'items': files}
        logger.info('Submitting async job for copying files in bulk')
        response = api.post(
            url=cls._URL['bulk_copy_files'], data=data
        ).json()
        return AsyncJob(api=api, **response)

    @classmethod
    def file_bulk_delete(cls, files, api=None):
        api = api or cls._API
        data = {'items': files}
        logger.info('Submitting async job for deleting files in bulk')
        response = api.post(
            url=cls._URL['bulk_delete_files'], data=data
        ).json()
        return AsyncJob(api=api, **response)
