import six

from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.billing.invoice_period import InvoicePeriod
from sevenbridges.models.compound.price import Price
from sevenbridges.meta.fields import (
    HrefField, StringField, BooleanField, CompoundField
)


class Invoice(Resource):
    """
     Central resource for managing invoices.
    """
    _URL = {
        'query': '/billing/invoices',
        'get': '/billing/invoices/{id}'
    }
    href = HrefField()
    id = StringField(read_only=True)
    pending = BooleanField(read_only=True)
    analysis_costs = CompoundField(Price, read_only=True)
    storage_costs = CompoundField(Price, read_only=True)
    total = CompoundField(Price, read_only=True)
    invoice_period = CompoundField(InvoicePeriod, read_only=True)

    def __str__(self):
        return six.text_type('<Invoice: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, offset=None, limit=None, api=None):
        """
        Query (List) invoices.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api if api else cls._API
        return super(Invoice, cls)._query(
            url=cls._URL['query'], offset=offset, limit=limit, fields='_all',
            api=api
        )
