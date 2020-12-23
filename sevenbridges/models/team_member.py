import logging

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
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    def __str__(self):
        return f'<Team member: username={self.username}>'
