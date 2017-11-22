import io
import logging
import os
import tempfile

import six

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import (
    ResourceNotModified, SbgError, LocalFileAlreadyExists
)
from sevenbridges.meta.fields import (
    HrefField, StringField, IntegerField, CompoundField, DateTimeField,
    BasicListField)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.compound.files.download_info import DownloadInfo
from sevenbridges.models.compound.files.file_origin import FileOrigin
from sevenbridges.models.compound.files.file_storage import FileStorage
from sevenbridges.models.compound.files.metadata import Metadata
from sevenbridges.models.enums import PartSize
from sevenbridges.transfer.download import Download
from sevenbridges.transfer.upload import Upload

logger = logging.getLogger(__name__)


class File(Resource):
    """
    Central resource for managing files.
    """
    _URL = {
        'query': '/files',
        'get': '/files/{id}',
        'delete': '/files/{id}',
        'copy': '/files/{id}/actions/copy',
        'download_info': '/files/{id}/download_info',
        'metadata': '/files/{id}/metadata',
        'tags': '/files/{id}/tags'
    }

    href = HrefField()
    id = StringField()
    name = StringField(read_only=False)
    size = IntegerField(read_only=True)
    project = StringField(read_only=True)
    created_on = DateTimeField(read_only=True)
    modified_on = DateTimeField(read_only=True)
    origin = CompoundField(FileOrigin, read_only=True)
    storage = CompoundField(FileStorage, read_only=True)
    metadata = CompoundField(Metadata, read_only=False)
    tags = BasicListField(read_only=False)

    def __str__(self):
        return six.text_type('<File: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def query(cls, project, names=None, metadata=None, origin=None, tags=None,
              offset=None, limit=None, api=None):
        """
        Query ( List ) projects
        :param project: Project id
        :param names: Name list
        :param metadata: Metadata query dict
        :param origin: Origin query dict
        :param tags: List of tags to filter on
        :param offset: Pagination offset
        :param limit: Pagination limit
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API

        project = Transform.to_project(project)
        query_params = {}

        if names is not None and isinstance(names, list):
            if len(names) == 0:
                names.append("")
            query_params['name'] = names

        metadata_params = {}
        if metadata and isinstance(metadata, dict):
            for k, v in metadata.items():
                metadata_params['metadata.' + k] = metadata[k]

        if tags:
            query_params['tag'] = tags

        query_params.update(metadata_params)

        origin_params = {}
        if origin and isinstance(origin, dict):
            for k, v in origin.items():
                origin_params['origin.' + k] = origin[k]

        query_params.update(origin_params)

        return super(File, cls)._query(
            api=api, url=cls._URL['query'], project=project, offset=offset,
            limit=limit, fields='_all', **query_params
        )

    @classmethod
    def upload(cls, path, project, file_name=None, overwrite=False, retry=5,
               timeout=10, part_size=PartSize.UPLOAD_MINIMUM_PART_SIZE,
               wait=True, api=None):

        """
        Uploads a file using multipart upload and returns an upload handle
        if the wait parameter is set to False. If wait is set to True it
        will block until the upload is completed.

        :param path: File path on local disc.
        :param project: Project identifier
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
        project = Transform.to_project(project)
        upload = Upload(
            path, project, file_name=file_name, overwrite=overwrite,
            retry_count=retry, timeout=timeout, part_size=part_size, api=api
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
        extra = {'resource': self.__class__.__name__, 'query': {
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

    def download(self, path, retry=5, timeout=10,
                 chunk_size=PartSize.DOWNLOAD_MINIMUM_PART_SIZE, wait=True,
                 overwrite=False):
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

        extra = {'resource': self.__class__.__name__, 'query': {
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
        modified_data = self._modified_data()
        if silent or bool(modified_data):
            # If metadata is to be set
            if 'metadata' in modified_data:
                if hasattr(self, '_method'):
                    self._api.put(
                        url=self._URL['metadata'].format(id=self.id),
                        data=modified_data['metadata']
                    )
                else:
                    self._api.patch(
                        url=self._URL['metadata'].format(id=self.id),
                        data=modified_data['metadata']
                    )
                modified_data.pop('metadata')
            if 'tags' in modified_data:
                self._api.put(
                    url=self._URL['tags'].format(id=self.id),
                    data=modified_data['tags']
                )
                modified_data.pop('tags')
            # Change everything else
            if bool(modified_data):
                self._api.patch(
                    url=self._URL['get'].format(id=self.id), data=modified_data
                )
        else:
            raise ResourceNotModified()

        return self.reload()

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

    # noinspection PyAttributeOutsideInit
    def reload(self):
        """
        Refreshes the file with the data from the server.
        """
        try:
            data = self._api.get(self.href, append_base=False).json()
            resource = File(api=self._api, **data)
        except Exception:
            try:
                data = self._api.get(
                    self._URL['get'].format(id=self.id)).json()
                resource = File(api=self._api, **data)
            except Exception:
                raise SbgError('Resource can not be refreshed!')

        self._data = resource._data
        self._dirty = resource._dirty

        # If file.metadata = value was executed
        # file object will have attribute _method='PUT', which tells us
        # to force overwrite of metadata on the server. This is metadata
        # specific. Once we reload the resource we delete the attribute
        # _method from the instance.
        try:
            delattr(self, '_method')
        except AttributeError:
            pass

    def content(self, path=None, overwrite=True):
        """
        Downloads file to the specified path or as temporary file
        and reads the file content in memory.
         Should not be used on very large files.

        :param path: Path for file download If omitted tmp file will be used.
        :param overwrite: Overwrite file if exists locally
        :return: File content.
        """

        if path:
            self.download(wait=True, path=path, overwrite=overwrite)
            with io.open(path, 'r') as fp:
                return fp.read()

        with tempfile.NamedTemporaryFile() as tmpfile:
            self.download(wait=True, path=tmpfile.name, overwrite=overwrite)
            with io.open(tmpfile.name, 'r') as fp:
                return fp.read()
