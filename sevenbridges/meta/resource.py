import os

import six

from sevenbridges.errors import SbgError
from sevenbridges.http.client import HttpClient
from sevenbridges.meta.data import DataContainer
from sevenbridges.meta.fields import Field


# noinspection PyProtectedMember
class ResourceMeta(type):
    """
    Metaclass for all resources, knows how to inject instance of API from
    class that contains classes with this meta. Class that contains this class
    has to have 'api' property which will be injected into class level
    API property of Resource class.

    Creates constructors for all resources and manages instantiation of
    resource fields.
    """

    def __new__(cls, name, bases, dct):
        # Attach fields object fo resource instance.
        fields = {}
        for k, v in dct.items():
            if isinstance(v, Field):
                if v.name is None:
                    fields[k] = v
                else:  # field has explicit name set in the field constructor
                    fields[v.name] = v
                if v.name is None:
                    v.name = k
        dct['_fields'] = fields

        if '__init__' not in dct:
            def init(self, **kwargs):
                self._api = kwargs.pop('api', None)
                try:
                    urls = self._URL
                except AttributeError:
                    urls = None
                self._data = DataContainer(urls=urls, api=self._api)
                self._dirty = {}
                for k, v in kwargs.items():
                    if k in fields:
                        value = fields[k].validate(v)
                        self._data[k] = value

            # get modified data from the instance
            def modified_data(self):
                return self._dirty

            def equals(self, other):
                return type(self) == type(other) and self._data == other._data

            if '__str__' not in dct:
                dct['__str__'] = lambda self: self.__class__.__name__
            if '__repr__' not in dct:
                if six.PY2:
                    dct['__repr__'] = lambda self: str(self).encode('utf-8')
                else:
                    dct['__repr__'] = lambda self: str(self)

            dct['__init__'] = init
            dct['equals'] = equals
            dct['_modified_data'] = modified_data

        return type.__new__(cls, name, bases, dct)

    def __get__(cls, obj, objtype=None):
        # SPHINX_DOC part is for generating documentation
        if not isinstance(obj, HttpClient) and not os.environ['SPHINX_DOC']:
            raise SbgError(message='Improperly configured client!')
        if obj is None:
            return cls
        cls._API = obj
        return cls


# noinspection PyProtectedMember,PyAttributeOutsideInit
class Resource(six.with_metaclass(ResourceMeta)):
    """
    Resource is base class for all resources, hiding implementation details
    of magic of injecting instance of API and common operations (like generic
    query).
    """
    _API = None

    def __init__(self, api):
        self.api = api

    @classmethod
    def _query(cls, **kwargs):
        """
        Generic query implementation that is used
        by the resources.
        """
        from sevenbridges.models.link import Link
        from sevenbridges.meta.collection import Collection

        #: :type: _HttpClient
        api = kwargs.pop('api', cls._API)
        url = kwargs.pop('url')
        response = api.get(url=url, params=kwargs)
        data = response.json()
        total = response.headers['x-total-matching-query']
        projects = [cls(api=api, **item) for item in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(
            resource=cls, href=href, total=total, items=projects,
            links=links, api=api
        )

    @classmethod
    def get(cls, id, api=None):
        """
        Fetches the resource from the server.
        :param id: Resource identifier
        :param api: sevenbridges Api instance.
        :return: Resource object.
        """
        if not id:
            raise SbgError('Invalid id value!')
        api = api if api else cls._API
        if 'get' in cls._URL:
            resource = api.get(url=cls._URL['get'].format(id=id)).json()
            return cls(api=api, **resource)
        else:
            raise SbgError('Unable to fetch resource!')

    def delete(self):
        """
        Deletes the resource on the server.
        """
        if 'delete' in self._URL:
            self._api.delete(url=self._URL['delete'].format(id=self.id))
        else:
            raise SbgError('Resource can not be deleted!')

    def reload(self):
        """
        Refreshes the resource with the data from the server.
        """
        try:
            data = self._api.get(self.href, append_base=False).json()
            resource = self.__class__(api=self._api, **data)
        except Exception:
            try:
                data = self._api.get(
                    self._URL['get'].format(id=self.id)).json()
                resource = self.__class__(api=self._api, **data)
            except Exception:
                raise SbgError('Resource can not be refreshed!')

        self._data = resource._data
        self._dirty = resource._dirty
        return self
