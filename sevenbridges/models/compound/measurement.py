from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField, FloatField, CompoundField


class StorageCost(Resource):
    """
    Storage cost resource contains breakdown information regarding the amount
    of cost and the currency used.
    """
    amount = FloatField(read_only=True)
    currency = StringField(read_only=True)

    def __str__(self):
        return (
            f'<Storage cost breakdown amount={self.amount}, '
            f'currency={self.currency}>'
        )


class Measurement(Resource):
    """
    Measurement resource contains an information regarding the size and the
    unit of a certain resource.
    """
    size = FloatField(read_only=True)
    unit = StringField(read_only=True)
    cost = CompoundField(StorageCost, read_only=True)

    def __str__(self):
        return f'<Measurement size={self.size}, unit={self.unit}>'
