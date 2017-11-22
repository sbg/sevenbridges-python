import six

from sevenbridges.meta.fields import HrefField, StringField
from sevenbridges.meta.resource import Resource


class Division(Resource):
    """
    Central resource for managing divisions.
    """
    _URL = {
        'query': '/divisions',
        'get': '/divisions/{id}',
    }

    href = HrefField()
    id = StringField(read_only=True)
    name = StringField(read_only=True)

    def __str__(self):
        return six.text_type('<Division: id={id}>'.format(id=self.id))

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def query(cls, offset=None, limit=None, api=None):
        """
        Query (List) divisions.

        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api if api else cls._API
        return super(Division, cls)._query(
            url=cls._URL['query'], offset=offset, limit=limit,
            fields='_all', api=api
        )

    @classmethod
    def get(cls, id, api=None):
        return super(Division, cls).get(id)

    def reload(self):
        super(Division, self).reload()

    def get_teams(self, offset=None, limit=None):
        return self._api.teams.query(
            division=self.id, offset=offset, limit=limit
        )
