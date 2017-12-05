import logging
import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import HrefField, StringField
from sevenbridges.meta.transformer import Transform

logger = logging.getLogger(__name__)


class User(Resource):
    """
    Central resource for managing tasks.
    """
    _URL = {
        'me': '/user',
        'get': '/users/{id}'
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

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.username == other.username

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type(
            '<User: username={username}>'.format(username=self.username)
        )

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
        return super(User, cls).get(id=user, api=api)
