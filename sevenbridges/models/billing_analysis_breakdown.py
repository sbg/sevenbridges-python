from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import (
    UuidField, CompoundField, StringField,
    DateTimeField, FloatField, BooleanField
)
from sevenbridges.models.compound.analysis_cost import AnalysisCost


class BillingGroupAnalysisBreakdown(Resource):
    _URL = {
        'query': '/billing/groups/{id}/breakdown/analysis'
    }

    project_name = StringField(read_only=True)
    analysis_app_name = StringField(read_only=True)
    analysis_name = StringField(read_only=True)
    analysis_type = StringField(read_only=True)
    analysis_id = UuidField(read_only=True)
    ran_by = StringField(read_only=True)
    analysis_status = StringField(read_only=True)
    analysis_cost = CompoundField(AnalysisCost, read_only=True)
    refunded_amount = FloatField(read_only=True)
    time_started = DateTimeField(read_only=True)
    time_finished = DateTimeField(read_only=True)
    project_locked = BooleanField(read_only=True)

    @classmethod
    def query(cls, bg_id, api=None, date_from=None, date_to=None,
              invoice_id=None, fields=None, offset=0, limit=50):
        """
        Query (List) billing group analysis breakdown. Date parameters must be
        string in format MM-DD-YYYY

        :param fields:
        :param invoice_id:
        :param date_to: include all analysis transactions charged before and
         including date_to
        :param date_from: include all analysis transactions charged after and
         including date_from
        :param bg_id: Billing Group ID
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API

        return super(BillingGroupAnalysisBreakdown, cls)._query(
            url=cls._URL['query'].format(id=bg_id), offset=offset, limit=limit,
            date_from=date_from, date_to=date_to, invoice_id=invoice_id,
            fields=fields, api=api
        )

    def __str__(self):
        return '<BillingGroupAnalysisBreakdown>'
