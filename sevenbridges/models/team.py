import logging

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import ResourceNotModified
from sevenbridges.meta.collection import Collection
from sevenbridges.meta.fields import HrefField, StringField
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.link import Link
from sevenbridges.models.team_member import TeamMember

logger = logging.getLogger(__name__)


class Team(Resource):
    """
    Central resource for managing teams.
    """
    _URL = {
        'query': '/teams',
        'get': '/teams/{id}',
        'members_query': '/teams/{id}/members',
        'members_get': '/teams/{id}/members/{member}',
    }

    href = HrefField(read_only=True)
    id = StringField(read_only=True)
    name = StringField(read_only=False)

    def __str__(self):
        return f'<Team: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    @classmethod
    def query(cls, division, list_all=False, offset=None, limit=None,
              api=None):
        """
        :param division: Division slug.
        :param list_all: List all teams in division.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        division = Transform.to_division(division)
        api = api if api else cls._API
        return super()._query(
            url=cls._URL['query'], division=division, _all=list_all,
            offset=offset, limit=limit, fields='_all', api=api
        )

    @classmethod
    def create(cls, name, division, api=None):
        """
        Create team within a division
        :param name:  Team name.
        :param division: Parent division.
        :param api: Api instance.
        :return: Team object.
        """

        division = Transform.to_division(division)
        api = api if api else cls._API
        data = {
            'name': name,
            'division': division
        }

        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Creating team', extra=extra)
        created_team = api.post(cls._URL['query'], data=data).json()
        return Team(api=api, **created_team)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the team on the server.
        :param inplace Apply edits on the current instance or get a new one.
        :return: Team instance.
        """
        modified_data = self._modified_data()
        if modified_data:
            extra = {
                'resource': type(self).__name__,
                'query': {
                    'id': self.id,
                    'modified_data': modified_data
                }
            }
            logger.info('Saving team', extra=extra)
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=modified_data).json()
            team = Team(api=self._api, **data)
            return team
        else:
            raise ResourceNotModified()

    def get_members(self, offset=None, limit=None):
        """
        Fetch team members for current team.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        """
        extra = {
            'resource': type(self).__name__,
            'query': {'id': self.id}
        }
        logger.info('Get team members', extra=extra)
        response = self._api.get(
            url=self._URL['members_query'].format(id=self.id),
            params={'offset': offset, 'limit': limit}
        )
        data = response.json()
        total = response.headers['x-total-matching-query']
        members = [TeamMember(api=self._api, **member) for member in
                   data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(resource=TeamMember, href=href, total=total,
                          items=members, links=links, api=self._api)

    def add_member(self, user):
        """
        Add member to team
        :param user: User object or user's username
        :return: Added user.
        """
        user = Transform.to_user(user)
        data = {
            'id': user
        }
        extra = {
            'resource': type(self).__name__,
            'query': {
                'id': self.id,
                'data': data,
            }
        }
        logger.info('Adding team member using id', extra=extra)
        response = self._api.post(
            url=self._URL['members_query'].format(id=self.id), data=data)
        member_data = response.json()
        return TeamMember(api=self._api, **member_data)

    def remove_member(self, user):
        """
        Remove member from the team.
        :param user: User to be removed.
        """
        member = Transform.to_user(user)
        extra = {
            'resource': type(self).__name__,
            'query': {
                'id': self.id,
                'user': user,
            }
        }
        logger.info('Removing team member', extra=extra)
        self._api.delete(
            url=self._URL['members_get'].format(id=self.id, member=member)
        )
