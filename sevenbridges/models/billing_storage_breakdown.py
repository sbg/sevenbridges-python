from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import (
    CompoundField, StringField, BooleanField
)
from sevenbridges.models.compound.measurement import Measurement


class BillingGroupStorageBreakdown(Resource):
    _URL = {
        'query': '/billing/groups/{id}/breakdown/storage'
    }

    project_name = StringField(read_only=True)
    project_created_by = StringField(read_only=True)
    location = StringField(read_only=True)
    active = CompoundField(Measurement, read_only=True)
    archived = CompoundField(Measurement, read_only=True)
    project_locked = BooleanField(read_only=True)

    @classmethod
    def query(cls, bg_id, api=None, date_from=None, date_to=None,
              invoice_id=None, fields=None, offset=0, limit=50):
        """
        Query (List) billing group storage breakdown. Date parameters must be
        string in format MM-DD-YYYY

        :param fields:
        :param invoice_id:
        :param date_to: include all storage transactions charged before and
         including date_to
        :param date_from: include all storage transactions charged after and
         including date_from
        :param bg_id: Billing Group ID
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API

        return super(BillingGroupStorageBreakdown, cls)._query(
            url=cls._URL['query'].format(id=bg_id), offset=offset, limit=limit,
            date_from=date_from, date_to=date_to, invoice_id=invoice_id,
            fields=fields, api=api
        )

    def __str__(self):
        return '<BillingGroupStorageBreakdown>'
