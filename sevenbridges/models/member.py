import logging

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
        return f'<Member: username={self.username}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return (
            self is other or
            self.id == other.id or
            self.username == other.username
        )

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves modification to the api server.
        """
        data = self._modified_data()
        data = data['permissions']
        if data:
            url = self.href + self._URL['permissions']
            extra = {'resource': type(self).__name__, 'query': data}
            logger.info('Modifying permissions', extra=extra)
            self._api.patch(url=url, data=data, append_base=False)
        else:
            raise ResourceNotModified()
