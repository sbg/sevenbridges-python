from sevenbridges.meta.fields import (
    HrefField, UuidField, StringField, BooleanField, CompoundField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.models.billing_analysis_breakdown import (
    BillingGroupAnalysisBreakdown
)
from sevenbridges.models.billing_breakdown import BillingGroupBreakdown
from sevenbridges.models.billing_storage_breakdown import (
    BillingGroupStorageBreakdown
)
from sevenbridges.models.billing_egress_breakdown import (
    BillingGroupEgressBreakdown
)
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
        return f'<BillingGroup: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

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
        return super()._query(
            url=cls._URL['query'], offset=offset, limit=limit, fields='_all',
            api=api
        )

    def breakdown(self):
        """
        Get Billing group breakdown for the current billing group.
        """
        return BillingGroupBreakdown.get(self.id, self._api)

    def analysis_breakdown(self, date_from=None, date_to=None, invoice_id=None,
                           fields=None, offset=0, limit=50):
        """
        Get Billing group analysis breakdown for the current billing group.
        """
        return BillingGroupAnalysisBreakdown.query(
            self.id, self._api, date_from, date_to, invoice_id, fields,
            offset, limit
        )

    def storage_breakdown(self, date_from=None, date_to=None, invoice_id=None,
                          fields=None, offset=0, limit=50):
        """
        Get Billing group storage breakdown for the current billing group.
        """
        return BillingGroupStorageBreakdown.query(
            self.id, self._api, date_from, date_to, invoice_id, fields,
            offset, limit
        )

    def egress_breakdown(self, date_from=None, date_to=None, invoice_id=None,
                         fields=None, offset=0, limit=50):
        """
        Get Billing group egress breakdown for the current billing group.
        """
        return BillingGroupEgressBreakdown.query(
            self.id, self._api, date_from, date_to, invoice_id, fields,
            offset, limit
        )
