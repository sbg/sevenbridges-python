import copy
import logging

import six

from sevenbridges.errors import SbgError
from sevenbridges.meta.fields import Field
from sevenbridges.meta.data import DataContainer
from sevenbridges.meta.transformer import Transform

logger = logging.getLogger(__name__)


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

    def __new__(mcs, name, bases, dct):
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
                urls = getattr(self, '_URL', None)
                self._data = DataContainer(urls=urls, api=self._api)
                self._dirty = {}
                for k, v in kwargs.items():
                    if k in fields:
                        value = fields[k].validate(v)
                        self._data[k] = value

                self._old = copy.deepcopy(self._data.data)

            def _data_diff(d1, d2):
                data = {}
                for key in d1.keys():
                    if key not in d2.keys():
                        continue
                    else:
                        if type(d1[key]) is dict:
                            inner_diff = _data_diff(d1[key], d2[key])
                            if inner_diff:
                                data[key] = inner_diff
                        else:
                            if d1[key] != d2[key]:
                                data[key] = d2[key]
                return data

            # get modified data from the instance
            def modified_data(self):
                difference = _data_diff(self._old, self._data.data)
                self._dirty.update(difference)
                return self._dirty

            def equals(self, other):
                if not hasattr(other, '__class__'):
                    return False
                if not self.__class__ == other.__class__:
                    return False
                return self is other or self._data == other._data

            def deepcopy(self):
                return self.__class__(api=self._api, **self._data.data)

            if '__str__' not in dct:
                dct['__str__'] = lambda self: self.__class__.__name__
            if '__repr__' not in dct:
                if six.PY2:
                    dct['__repr__'] = lambda self: str(self).encode('utf-8')
                else:
                    dct['__repr__'] = lambda self: str(self)

            dct['__init__'] = init
            dct['equals'] = equals
            dct['deepcopy'] = deepcopy
            dct['_modified_data'] = modified_data

        return type.__new__(mcs, name, bases, dct)

    def __get__(cls, obj, objtype=None):
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

        api = kwargs.pop('api', cls._API)
        url = kwargs.pop('url')
        extra = {'resource': cls.__name__, 'query': kwargs}
        logger.info('Querying {} resource'.format(cls), extra=extra)
        response = api.get(url=url, params=kwargs)
        data = response.json()
        total = response.headers['x-total-matching-query']

        items = [cls(api=api, **item) for item in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(
            resource=cls, href=href, total=total, items=items,
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
        id = Transform.to_resource(id)
        api = api if api else cls._API
        if 'get' in cls._URL:
            extra = {'resource': cls.__name__, 'query': {'id': id}}
            logger.info('Fetching {} resource'.format(cls), extra=extra)
            resource = api.get(url=cls._URL['get'].format(id=id)).json()
            return cls(api=api, **resource)
        else:
            raise SbgError('Unable to retrieve resource!')

    def delete(self):
        """
        Deletes the resource on the server.
        """
        if 'delete' in self._URL:
            extra = {'resource': self.__class__.__name__, 'query': {
                'id': self.id}}
            logger.info("Deleting {} resource.".format(self), extra=extra)
            self._api.delete(url=self._URL['delete'].format(id=self.id))
        else:
            raise SbgError('Resource can not be deleted!')

    def reload(self):
        """
        Refreshes the resource with the data from the server.
        """
        try:
            if hasattr(self, 'href'):
                data = self._api.get(self.href, append_base=False).json()
                resource = self.__class__(api=self._api, **data)
            elif hasattr(self, 'id') and hasattr(self, '_URL') and \
                    'get' in self._URL:
                data = self._api.get(
                    self._URL['get'].format(id=self.id)).json()
                resource = self.__class__(api=self._api, **data)
            else:
                raise SbgError(
                    'Resource can not be refreshed, "id" property not set or '
                    'retrieval for this resource is not available.'
                )
            query = {'id': self.id} if hasattr(self, 'id') else {}
            extra = {'resource': self.__class__.__name__, 'query': query}
            logger.info('Reloading {} resource.'.format(self), extra=extra)
        except Exception as e:
            raise SbgError(
                'Resource can not be refreshed due to an error: {}'
                .format(six.text_type(e))
            )

        self._data = resource._data
        self._dirty = resource._dirty
        self._old = copy.deepcopy(self._data.data)
        return self

    def field(self, name):
        """
        Return field value if it's set
        :param name: Field name
        :return: Field value or None
        """
        return self._data.data.get(name, None)
