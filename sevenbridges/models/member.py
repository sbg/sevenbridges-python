import logging

import six

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import ResourceNotModified
from sevenbridges.meta.fields import HrefField, StringField, CompoundField
from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.projects.permissions import Permissions

logger = logging.getLogger(__name__)


class Member(Resource):
    """
    Central resource for managing members.
    This resource is reused on both projects and volumes.
    """
    _URL = {
        'permissions': '/permissions'
    }
    href = HrefField()
    id = StringField(read_only=True)
    username = StringField(read_only=False)
    email = StringField(read_only=False)
    type = StringField(read_only=False)
    permissions = CompoundField(Permissions, read_only=False)

    def __str__(self):
        return six.text_type(
            '<Member: username={username}>'.format(username=self.username)
        )

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return (
            self is other or
            self.id == other.id or
            self.username == other.username
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves modification to the api server.
        """
        data = self._modified_data()
        data = data['permissions']
        if bool(data):
            url = six.text_type(self.href) + self._URL['permissions']
            extra = {'resource': self.__class__.__name__, 'query': data}
            logger.info('Modifying permissions', extra=extra)
            self._api.patch(url=url, data=data, append_base=False)
        else:
            raise ResourceNotModified()
