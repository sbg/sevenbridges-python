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
        return f'<Division: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

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
        return super()._query(
            url=cls._URL['query'], offset=offset, limit=limit,
            fields='_all', api=api
        )

    def get_teams(self, offset=None, limit=None):
        return self._api.teams.query(
            division=self.id, offset=offset, limit=limit
        )

    def get_members(self, role=None, offset=None, limit=None):
        return self._api.users.query(self, role=role, offset=offset,
                                     limit=limit)
