import re

import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.meta.fields import (
    HrefField, StringField, IntegerField, DictField
)


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
        'raw': '/apps/{id}/raw'
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
        if re.match('^\d*$', _rev):
            return _id
        else:
            return self._id

    def __str__(self):
        return six.text_type('<App: id={id} rev={rev}>'.format(
            id=self.id, rev=self.revision)
        )

    @classmethod
    def query(cls, project=None, visibility=None, offset=None, limit=None,
              api=None):
        """
        Query (List) apps.
        :param visibility:
        :param project:
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: collection object
        """
        if project:
            project = Transform.to_project(project)
        api = api or cls._API
        return super(App, cls)._query(url=cls._URL['query'], project=project,
                                      visibility=visibility,
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
        app = api.get(url=cls._URL['get_revision'].format(
            id=id, revision=revision)).json()
        return App(api=api, **app)

    @classmethod
    def install_app(cls, id, raw, api=None):
        """
        Installs and app.
        :param id:  App identifier.
        :param raw: Raw cwl data.
        :param api: Api instance.
        :return: App object.
        """
        api = api if api else cls._API
        app = api.post(url=cls._URL['raw'].format(id=id), data=raw).json()
        app_wrapper = api.get(url=cls._URL['get'].format(
            id=app['sbg:id'])).json()
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
        app = api.post(url=cls._URL['create_revision'].format(
            id=id, revision=revision), data=raw).json()
        app_wrapper = api.get(
            url=cls._URL['get'].format(id=app['sbg:id'])).json()
        return App(api=api, **app_wrapper)

    def copy(self, project, name=None):
        """
        Copies the current app.
        :param project: Destination project.
        :param name: Destination app name.
        :return: Copied App object.
        """

        project = Transform.to_project(project)
        data = {
            'project': project
        }
        if name:
            data['name'] = name

        app = self._api.post(url=self._URL['copy'].format(id=self.id),
                             data=data).json()
        return App(api=self._api, **app)
