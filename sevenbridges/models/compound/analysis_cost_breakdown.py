from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import FloatField


class AnalysisCostBreakdown(Resource):
    """
    AnalysisCostBreakdown resource contains price breakdown by storage and
    computation.
    """
    storage = FloatField(read_only=True)
    computation = FloatField(read_only=True)
    data_transfer_in = FloatField(read_only=True)

    def __str__(self):
        return (
            f'<AnalysisCostBreakdown: storage={self.storage}, '
            f'computation={self.computation}, '
            f'data_transfer_in={self.data_transfer_in}'
        )
