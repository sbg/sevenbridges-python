from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class EgressCost(Resource):
    """
    EgressCost resource contains an information regarding the currency and the
    monet value of a egress cost.
    """
    currency = StringField(read_only=True)
    amount = StringField(read_only=True)

    def __str__(self):
        return f'<EgressCost: currency={self.currency}, amount={self.amount}>'
