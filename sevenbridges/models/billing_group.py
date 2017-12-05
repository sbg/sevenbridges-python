import six

from sevenbridges.meta.fields import (
    HrefField, UuidField, StringField, BooleanField, CompoundField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.models.billing_breakdown import BillingGroupBreakdown
from sevenbridges.models.compound.price import Price


class BillingGroup(Resource):
    """
    Central resource for managing billing groups.
    """
    _URL = {
        'query': '/billing/groups',
        'get': '/billing/groups/{id}'
    }
    href = HrefField()
    id = UuidField()
    owner = StringField(read_only=True)
    name = StringField(read_only=True)
    type = StringField(read_only=True)
    pending = BooleanField(read_only=True)
    disabled = BooleanField(read_only=False)
    balance = CompoundField(Price, read_only=True)

    def __str__(self):
        return six.text_type('<BillingGroup: id={id}>'.format(id=self.id))

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
        Query (List) billing group.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :return: Collection object.
        :param api: Api instance.
        """
        api = api or cls._API
        return super(BillingGroup, cls)._query(
            url=cls._URL['query'], offset=offset, limit=limit, fields='_all',
            api=api
        )

    def breakdown(self):
        """
        Get Billing group breakdown for the current billing group.
        """
        return BillingGroupBreakdown.get(self.id, self._api)
