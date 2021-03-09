import os
import logging
import tempfile

from sevenbridges.errors import (
    SbgError,
    ResourceNotModified,
    LocalFileAlreadyExists
)
from sevenbridges.meta.fields import (
    HrefField, StringField, IntegerField, CompoundField, DateTimeField,
    BasicListField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.models.bulk import BulkRecord
from sevenbridges.transfer.upload import Upload
from sevenbridges.decorators import inplace_reload
from sevenbridges.transfer.download import Download
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.files.metadata import Metadata
from sevenbridges.models.enums import PartSize, RequestParameters
from sevenbridges.models.compound.files.file_storage import FileStorage
from sevenbridges.models.compound.files.file_origin import FileOrigin
from sevenbridges.models.compound.files.download_info import DownloadInfo

logger = logging.getLogger(__name__)


class File(Resource):
    """
    Central resource for managing files.
    """
    FOLDER_TYPE = 'folder'

    _URL = {
        'query': '/files',
        'scroll': '/files/scroll',
        'get': '/files/{id}',
        'delete': '/files/{id}',
        'copy': '/files/{id}/actions/copy',
        'download_info': '/files/{id}/download_info',
        'metadata': '/files/{id}/metadata',
        'tags': '/files/{id}/tags',

        'bulk_get': '/bulk/files/get',
        'bulk_delete': '/bulk/files/delete',
        'bulk_update': '/bulk/files/update',
        'bulk_edit': '/bulk/files/edit',

        'create_folder': '/files',
        'list_folder': '/files/{id}/list',
        'scroll_folder': '/files/{id}/scroll',
        'copy_to_folder': '/files/{file_id}/actions/copy',
        'move_to_folder': '/files/{file_id}/actions/move',
    }

    href = HrefField(read_only=True)
    id = StringField(read_only=True)
    type = StringField(read_only=True)
    name = StringField(read_only=False)
    size = IntegerField(read_only=True)
    parent = StringField(read_only=True)
    project = StringField(read_only=True)
    created_on = DateTimeField(read_only=True)
    modified_on = DateTimeField(read_only=True)
    origin = CompoundField(FileOrigin, read_only=True)
    storage = CompoundField(FileStorage, read_only=True)
    metadata = CompoundField(Metadata, read_only=False)
    tags = BasicListField(read_only=False)
    _secondary_files = BasicListField(read_only=False, name='_secondary_files')

    def __str__(self):
        return f'<File: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    def is_folder(self):
        return self.type.lower() == self.FOLDER_TYPE

    @property
    def secondary_files(self):
        if self.field('_secondary_files'):
            return [
                File(api=self._api, **data)
                for data in self._secondary_files
            ]

    @classmethod
    def query(cls, project=None, names=None, metadata=None, origin=None,
              tags=None, offset=None, limit=None, dataset=None,
              api=None, parent=None, cont_token=None):
        """
        Query ( List ) files, requires project or dataset
        :param project: Project id
        :param names: Name list
        :param metadata: Metadata query dict
        :param origin: Origin query dict
        :param tags: List of tags to filter on
        :param offset: Pagination offset
        :param limit: Pagination limit
        :param dataset: Dataset id
        :param api: Api instance.
        :param parent: Folder id or File object with type folder
        :param cont_token: Pagination continuation token
        :return: Collection object.
        """

        if cont_token and offset:
            raise SbgError(
                'Offset and continuation token parameters'
                'are mutually exclusive.'
            )

        if cont_token and metadata:
            raise SbgError(
                'Metadata filtering cannot be combined '
                'with continuation token pagination.'
            )

        api = api or cls._API

        query_params = {}

        if project:
            project = Transform.to_project(project)
            query_params['project'] = project

        if dataset:
            dataset = Transform.to_dataset(dataset)
            query_params['dataset'] = dataset

        if parent:
            query_params['parent'] = Transform.to_file(parent)

        if not (project or dataset or parent):
            raise SbgError('Project, dataset or parent must be provided.')

        if [project, parent, dataset].count(None) < 2:
            raise SbgError(
                'Only one out of project, parent or dataset must be provided.'
            )

        if names is not None and isinstance(names, list):
            if len(names) == 0:
                names.append("")
            query_params['name'] = names

        metadata_params = {}
        if metadata and isinstance(metadata, dict):
            for k, v in metadata.items():
                metadata_params[f'metadata.{k}'] = metadata[k]

        if tags:
            query_params['tag'] = tags

        query_params.update(metadata_params)

        origin_params = {}
        if origin and isinstance(origin, dict):
            for k, v in origin.items():
                origin_params[f'origin.{k}'] = origin[k]

        query_params.update(origin_params)

        return super()._query(
            api=api, url=cls._URL['scroll' if cont_token else 'query'],
            token=cont_token, offset=offset,
            limit=limit, fields='_all', **query_params
        )

    @classmethod
    def upload(cls, path, project=None, parent=None, file_name=None,
               overwrite=False, retry=RequestParameters.DEFAULT_RETRY_COUNT,
               timeout=RequestParameters.DEFAULT_TIMEOUT, part_size=None,
               wait=True, api=None):
        """
        Uploads a file using multipart upload and returns an upload handle
        if the wait parameter is set to False. If wait is set to True it
        will block until the upload is completed.

        :param path: File path on local disc.
        :param project: Project identifier
        :param parent: Parent folder identifier
        :param file_name: Optional file name.
        :param overwrite: If true will overwrite the file on the server.
        :param retry:  Number of retries if error occurs during upload.
        :param timeout:  Timeout for http requests.
        :param part_size:  Part size in bytes.
        :param wait:  If true will wait for upload to complete.
        :param api: Api instance.
        """

        api = api or cls._API
        extra = {'resource': cls.__name__, 'query': {
            'path': path,
            'project': project,
            'file_name': file_name,
            'overwrite': overwrite,
            'retry': retry,
            'timeout': timeout,
            'part_size': part_size,
            'wait': wait,
        }}
        logger.info('Uploading file', extra=extra)

        if not project and not parent:
            raise SbgError('A project or parent identifier is required.')

        if project and parent:
            raise SbgError(
                'Project and parent identifiers are mutually exclusive.'
            )

        if project:
            project = Transform.to_project(project)

        if parent:
            parent = Transform.to_file(parent)

        upload = Upload(
            file_path=path, project=project, parent=parent,
            file_name=file_name, overwrite=overwrite, retry_count=retry,
            timeout=timeout, part_size=part_size, api=api
        )
        if wait:
            upload.start()
            upload.wait()
            return upload
        else:
            return upload

    def copy(self, project, name=None):
        """
        Copies the current file.
        :param project: Destination project.
        :param name: Destination file name.
        :return: Copied File object.
        """
        project = Transform.to_project(project)
        data = {
            'project': project
        }
        if name:
            data['name'] = name
        extra = {'resource': type(self).__name__, 'query': {
            'id': self.id,
            'data': data
        }}
        logger.info('Copying file', extra=extra)
        new_file = self._api.post(url=self._URL['copy'].format(id=self.id),
                                  data=data).json()
        return File(api=self._api, **new_file)

    def download_info(self):
        """
        Fetches download information containing file url
        that can be used to download file.
        :return: Download info object.
        """
        info = self._api.get(url=self._URL['download_info'].format(id=self.id))
        return DownloadInfo(api=self._api, **info.json())

    def download(self, path, retry=RequestParameters.DEFAULT_RETRY_COUNT,
                 timeout=RequestParameters.DEFAULT_TIMEOUT, chunk_size=None,
                 wait=True, overwrite=False):
        """
        Downloads the file and returns a download handle.
        Download will not start until .start() method is invoked.
        :param path: Full path to the new file.
        :param retry:  Number of retries if error occurs during download.
        :param timeout:  Timeout for http requests.
        :param chunk_size:  Chunk size in bytes.
        :param wait: If true will wait for download to complete.
        :param overwrite: If True will silently overwrite existing file.
        :return: Download handle.
        """

        if not overwrite and os.path.exists(path):
            raise LocalFileAlreadyExists(message=path)

        extra = {'resource': type(self).__name__, 'query': {
            'id': self.id,
            'path': path,
            'overwrite': overwrite,
            'retry': retry,
            'timeout': timeout,
            'chunk_size': chunk_size,
            'wait': wait,
        }}
        logger.info('Downloading file', extra=extra)
        info = self.download_info()
        download = Download(
            url=info.url, file_path=path, retry_count=retry, timeout=timeout,
            part_size=chunk_size, api=self._api
        )
        if wait:
            download.start()
            download.wait()
        else:
            return download

    @inplace_reload
    def save(self, inplace=True, silent=False):
        """
        Saves all modification to the file on the server. By default this
        method raises an error if you are trying to save an instance that was
        not changed. Set check_if_modified param to False to disable
        this behaviour.
        :param inplace: Apply edits to the current instance or get a new one.
        :param silent: If Raises exception if file wasn't modified.
        :raise ResourceNotModified
        :return: File instance.
        """
        reload = False
        modified_data = self._modified_data()
        if not (silent or modified_data):
            raise ResourceNotModified()

        # Update metadata
        if 'metadata' in modified_data:
            if hasattr(self, '_overwrite_metadata'):
                self.metadata = self._api.put(
                    url=self._URL['metadata'].format(id=self.id),
                    data=modified_data['metadata']
                ).json()
                delattr(self, '_overwrite_metadata')
            else:
                self.metadata = self._api.patch(
                    url=self._URL['metadata'].format(id=self.id),
                    data=modified_data['metadata']
                ).json()
            reload = True
            modified_data.pop('metadata')

        # Update tags
        if 'tags' in modified_data:
            self.tags = self._api.put(
                url=self._URL['tags'].format(id=self.id),
                data=modified_data['tags']
            ).json()
            reload = True
            modified_data.pop('tags')

        # Update everything else
        if modified_data:
            data = self._api.patch(
                url=self._URL['get'].format(id=self.id), data=modified_data
            ).json()
            self._update_read_only(data)

        return self if not reload else self.reload()

    def stream(self, part_size=32 * PartSize.KB):
        """
        Creates an iterator which can be used to stream the file content.
        :param part_size: Size of the part in bytes. Default 32KB
        :return Iterator
        """
        download_info = self.download_info()
        response = self._api.get(
            url=download_info.url, stream=True, append_base=False
        )
        for part in response.iter_content(part_size):
            yield part

    def reload(self):
        """
        Refreshes the file with the data from the server.
        """
        # Use standard resource reload
        super().reload()

        # If file.metadata = value was executed
        # file object will have attribute _overwrite_metadata=True,
        # which tells us to force overwrite of metadata on the server.
        # This is metadata specific. Once we reload the resource we delete the
        # attribute _overwrite_metadata from the instance.
        if hasattr(self, '_overwrite_metadata'):
            delattr(self, '_overwrite_metadata')

        return self

    def content(self, path=None, overwrite=True, encoding='utf-8'):
        """
        Downloads file to the specified path or as temporary file
        and reads the file content in memory.
         Should not be used on very large files.

        :param path: Path for file download If omitted tmp file will be used.
        :param overwrite: Overwrite file if exists locally
        :param encoding: File encoding, by default it is UTF-8
        :return: File content.
        """
        if path:
            self.download(wait=True, path=path, overwrite=overwrite)
            with open(path, 'r', encoding=encoding) as fp:
                return fp.read()

        with tempfile.NamedTemporaryFile() as tmpfile:
            self.download(wait=True, path=tmpfile.name, overwrite=overwrite)
            with open(tmpfile.name, 'r', encoding=encoding) as fp:
                return fp.read()

    @classmethod
    def bulk_get(cls, files, api=None):
        """
        Retrieve files with specified ids in bulk
        :param files: Files to be retrieved.
        :param api: Api instance.
        :return: List of FileBulkRecord objects.
        """
        api = api or cls._API
        file_ids = [Transform.to_file(file_) for file_ in files]
        data = {'file_ids': file_ids}

        logger.debug('Getting files in bulk.')
        response = api.post(url=cls._URL['bulk_get'], data=data)
        return FileBulkRecord.parse_records(response=response, api=api)

    @classmethod
    def bulk_delete(cls, files, api=None):
        """
        Delete files with specified ids in bulk
        :param files: Files to be deleted.
        :param api: Api instance.
        :return: List of FileBulkRecord objects.
        """
        api = api or cls._API
        file_ids = [Transform.to_file(file_) for file_ in files]
        data = {'file_ids': file_ids}

        logger.debug('Deleting files in bulk.')
        response = api.post(url=cls._URL['bulk_delete'], data=data)
        return FileBulkRecord.parse_records(response=response, api=api)

    @classmethod
    def bulk_update(cls, files, api=None):
        """
        This call updates the details for multiple specified files.
        Use this call to set new information for the files, thus replacing
        all existing information and erasing omitted parameters. For each
        of the specified files, the call sets a new name, new tags and
        metadata.
        :param files: List of file instances.
        :param api: Api instance.
        :return: List of FileBulkRecord objects.
        """
        if not files:
            raise SbgError('Files are required.')

        api = api or cls._API
        data = {
            'items': [
                {
                    'id': file_.id,
                    'name': file_.name,
                    'tags': file_.tags,
                    'metadata': file_.metadata,
                }
                for file_ in files
            ]
        }

        logger.debug('Updating files in bulk.')
        response = api.post(url=cls._URL['bulk_update'], data=data)
        return FileBulkRecord.parse_records(response=response, api=api)

    @classmethod
    def bulk_edit(cls, files, api=None):
        """
        This call edits the details for multiple specified files.
        Use this call to modify the existing information for the files
        or add new information while preserving omitted parameters.
        For each of the specified files, the call edits its name, tags
        and metadata.
        :param files: List of file instances.
        :param api: Api instance.
        :return: List of FileBulkRecord objects.
        """
        if not files:
            raise SbgError('Files are required.')

        api = api or cls._API
        data = {
            'items': [
                {
                    'id': file_.id,
                    'name': file_.name,
                    'tags': file_.tags,
                    'metadata': file_.metadata,
                }
                for file_ in files
            ]
        }

        logger.debug('Editing files in bulk.')
        response = api.post(url=cls._URL['bulk_edit'], data=data)
        return FileBulkRecord.parse_records(response=response, api=api)

    def list_files(self, offset=None, limit=None, api=None, cont_token=None):
        """List files in a folder
        :param api: Api instance
        :param offset: Pagination offset
        :param limit: Pagination limit
        :param cont_token: Pagination continuation token
        :return: List of files
        """

        if cont_token and offset:
            raise SbgError(
                'Offset and continuation token parameters'
                'are mutually exclusive.'
            )

        api = api or self._API

        if not self.is_folder():
            raise SbgError(f'{self.name} is not a folder')

        url = self._URL[
            'scroll_folder' if cont_token else 'list_folder'
        ].format(id=self.id)

        return super(File, type(self))._query(
            api=api, url=url, token=cont_token, offset=offset,
            limit=limit, fields='_all'
        )

    @classmethod
    def create_folder(cls, name, parent=None, project=None,
                      api=None):
        """Create a new folder
        :param name: Folder name
        :param parent: Parent folder
        :param project: Project to create folder in
        :param api: Api instance
        :return: New folder
        """
        api = api or cls._API

        data = {
            'name': name,
            'type': cls.FOLDER_TYPE
        }

        if not parent and not project:
            raise SbgError('Parent or project must be provided')

        if parent and project:
            raise SbgError(
                'Providing both "parent" and "project" is not allowed'
            )

        if parent:
            data['parent'] = Transform.to_file(file_=parent)

        if project:
            data['project'] = Transform.to_project(project=project)

        response = api.post(url=cls._URL['create_folder'], data=data).json()
        return cls(api=api, **response)

    def copy_to_folder(self, parent, name=None, api=None):
        """Copy file to folder
        :param parent: Folder to copy file to
        :param name: New file name
        :param api: Api instance
        :return: New file instance
        """
        api = api or self._API

        if self.is_folder():
            raise SbgError('Copying folders is not supported')

        data = {
            'parent': Transform.to_file(parent)
        }

        if name:
            data['name'] = name

        response = api.post(
            url=self._URL['copy_to_folder'].format(file_id=self.id),
            data=data
        ).json()
        return File(api=api, **response)

    def move_to_folder(self, parent, name=None, api=None):
        """Move file to folder
        :param parent: Folder to move file to
        :param name: New file name
        :param api: Api instance
        :return: New file instance
        """
        api = api or self._API

        if self.is_folder():
            raise SbgError('Moving folders is not supported')

        data = {
            'parent': Transform.to_file(parent)
        }

        if name:
            data['name'] = name

        response = api.post(
            url=self._URL['move_to_folder'].format(file_id=self.id),
            data=data
        ).json()
        return File(api=api, **response)


class FileBulkRecord(BulkRecord):
    resource = CompoundField(cls=File, read_only=False)

    def __str__(self):
        return f'<FileBulkRecord valid={self.valid}>'
