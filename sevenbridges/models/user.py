import logging

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import HrefField, StringField
from sevenbridges.meta.transformer import Transform

logger = logging.getLogger(__name__)


class User(Resource):
    """
    Central resource for managing users.
    """
    _URL = {
        'me': '/user',
        'get': '/users/{id}',
        'query': '/users',
        'delete': '/users/{username}'
    }

    href = HrefField()
    username = StringField(read_only=True)
    email = StringField(read_only=True)
    first_name = StringField(read_only=True)
    last_name = StringField(read_only=True)
    affiliation = StringField(read_only=True)
    phone = StringField(read_only=True)
    address = StringField(read_only=True)
    state = StringField(read_only=True)
    country = StringField(read_only=True)
    zip_code = StringField(read_only=True)
    city = StringField(read_only=True)
    role = StringField(read_only=True)

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.username == other.username

    def __str__(self):
        return f'<User: username={self.username}>'

    @classmethod
    def me(cls, api=None):
        """
        Retrieves current user information.
        :param api: Api instance.
        :return: User object.
        """
        api = api if api else cls._API
        extra = {
            'resource': cls.__name__,
            'query': {}
        }
        logger.info('Fetching user information', extra=extra)
        user_data = api.get(cls._URL['me']).json()
        return User(api=api, **user_data)

    @classmethod
    def get(cls, user, api=None):
        api = api if api else cls._API
        user = Transform.to_user(user)
        return super().get(id=user, api=api)

    @classmethod
    def query(cls, division, role=None, offset=None, limit=None, api=None):
        """Query division users
        :param division: Division slug.
        :param role: User role in division.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API
        params = {
            'division': Transform.to_division(division),
        }
        if role:
            params['role'] = role

        return super()._query(
            url=cls._URL['query'],
            api=api,
            offset=offset,
            limit=limit,
            **params
        )

    def disable(self, api=None):
        """
        Disable user
        :param api: Api instance.
        :return:
        """
        api = api or self._API
        api.delete(
            url=self._URL['delete'].format(username=self.username)
        )
