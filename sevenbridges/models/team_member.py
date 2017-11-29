import logging

import six

from sevenbridges.meta.fields import HrefField, StringField
from sevenbridges.meta.resource import Resource

logger = logging.getLogger(__name__)


class TeamMember(Resource):
    """
    Central resource for managing team members.
    """
    href = HrefField()
    id = StringField(read_only=True)
    username = StringField(read_only=False)
    role = StringField(read_only=True)

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return six.text_type('<Team member: username={username}>'
                             .format(username=self.username))
