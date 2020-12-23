import logging
import re

from sevenbridges.meta.fields import (
    DictField,
    HrefField,
    StringField,
    IntegerField,
)
from sevenbridges.errors import SbgError
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.enums import AppRawFormat, AppCopyStrategy

logger = logging.getLogger(__name__)


class App(Resource):
    """
    Central resource for managing apps.
    """
    _URL = {
        'query': '/apps',
        'get': '/apps/{id}',
        'get_revision': '/apps/{id}/{revision}',
        'create_revision': '/apps/{id}/{revision}/raw',
        'copy': '/apps/{id}/actions/copy',
        'sync': '/apps/{id}/actions/sync',
        'raw': '/apps/{id}/raw'
    }

    _CONTENT_TYPE = {
        AppRawFormat.JSON: 'application/json',
        AppRawFormat.YAML: 'application/yaml'
    }

    href = HrefField()
    _id = StringField(read_only=True, name='id')
    project = StringField(read_only=True)
    name = StringField(read_only=True)
    revision = IntegerField(read_only=True)
    raw = DictField(read_only=False)

    @property
    def id(self):
        _id, _rev = self._id.rsplit('/', 1)
        if re.match(r'^\d*$', _rev):
            return _id
        else:
            return self._id

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    def __str__(self):
        revision = self.field('revision')
        if revision:
            return f'<App: id={self.id} rev={self.revision}>'
        return f'<App: id={self.id}'

    @classmethod
    def query(cls, project=None, visibility=None, q=None, id=None, offset=None,
              limit=None, api=None):
        """
        Query (List) apps.
        :param project: Source project.
        :param visibility: private|public for private or public apps.
        :param q: List containing search terms.
        :param id: List contains app ids. Fetch apps with specific ids.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: collection object
        """
        if project:
            project = Transform.to_project(project)
        api = api or cls._API
        return super()._query(url=cls._URL['query'], project=project,
                              visibility=visibility, q=q, id=id,
                              offset=offset, limit=limit, api=api)

    @classmethod
    def get_revision(cls, id, revision, api=None):
        """
        Get app revision.
        :param id: App identifier.
        :param revision: App revision
        :param api: Api instance.
        :return: App object.
        """
        api = api if api else cls._API
        extra = {'resource': cls.__name__, 'query': {
            'id': id,
            'revision': revision
        }}
        logger.info('Get revision', extra=extra)
        app = api.get(url=cls._URL['get_revision'].format(
            id=id, revision=revision)).json()
        return App(api=api, **app)

    @classmethod
    def install_app(cls, id, raw, api=None, raw_format=None):
        """
        Installs and app.
        :param id:  App identifier.
        :param raw: Raw cwl data.
        :param api: Api instance.
        :param raw_format: Format of raw app data being sent, json by default
        :return: App object.
        """
        api = api if api else cls._API
        raw_format = raw_format.lower() if raw_format else AppRawFormat.JSON
        extra = {
            'resource': cls.__name__,
            'query': {
                'id': id,
                'data': raw
            }
        }
        logger.info('Installing app', extra=extra)

        # Set content type for raw app data
        if raw_format not in cls._CONTENT_TYPE.keys():
            raise SbgError(f'Unsupported raw data format: "{raw_format}".')
        headers = {'Content-Type': cls._CONTENT_TYPE[raw_format]}

        app = api.post(
            url=cls._URL['raw'].format(id=id),
            data=raw,
            headers=headers,
        ).json()
        app_wrapper = api.get(
            url=cls._URL['get'].format(id=app['sbg:id'])).json()
        return App(api=api, **app_wrapper)

    @classmethod
    def create_revision(cls, id, revision, raw, api=None):
        """
        Create a new app revision.
        :param id:  App identifier.
        :param revision: App revision.
        :param raw: Raw cwl object.
        :param api: Api instance.
        :return: App object.
        """

        api = api if api else cls._API
        extra = {'resource': cls.__name__, 'query': {
            'id': id,
            'data': raw
        }}
        logger.info('Creating app revision', extra=extra)
        app = api.post(url=cls._URL['create_revision'].format(
            id=id, revision=revision), data=raw).json()
        app_wrapper = api.get(
            url=cls._URL['get'].format(id=app['sbg:id'])).json()
        return App(api=api, **app_wrapper)

    def copy(self, project, name=None, strategy=None, use_revision=False,
             api=None):
        """
        Copies the current app.
        :param project: Destination project.
        :param name: Destination app name.
        :param strategy: App copy strategy.
        :param use_revision: Copy from set app revision.
        :param api: Api instance.
        :return: Copied App object.

        :Copy strategies:
        clone         copy all revisions and continue getting updates form the
                      original app (default method when the key is omitted)

        direct        copy only the latest revision and get the updates from
                      this point on

        clone_direct  copy the app like the direct strategy, but keep all
                      revisions

        transient     copy only the latest revision and continue getting
                      updates from the original app
        """
        api = api or self._API
        app_id = self._id if use_revision else self.id
        strategy = strategy or AppCopyStrategy.CLONE

        project = Transform.to_project(project)
        data = {
            'project': project,
            'strategy': strategy
        }
        if name:
            data['name'] = name
        extra = {
            'resource': type(self).__name__,
            'query': {
                'id': app_id,
                'data': data
            }
        }
        logger.info('Copying app', extra=extra)
        app = api.post(
            url=self._URL['copy'].format(id=app_id), data=data
        ).json()
        return App(api=api, **app)

    def sync(self):
        """
        Syncs the parent app changes with the current app instance.
        :return: Synced App object.
        """
        app = self._api.post(url=self._URL['sync'].format(id=self.id)).json()
        return App(api=self._api, **app)
