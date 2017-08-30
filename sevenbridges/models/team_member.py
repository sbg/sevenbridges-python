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
        if self is other:
            return True
        else:
            return self.id == other.id and self.__class__ == other.__class__

    def __str__(self):
        return six.text_type('<Team member: username={username}>'
                             .format(username=self.username))
