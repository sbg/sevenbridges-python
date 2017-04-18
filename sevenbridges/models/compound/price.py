import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField, FloatField, CompoundField
from sevenbridges.models.compound.price_breakdown import Breakdown


class Price(Resource):
    """
    Price resource contains an information regarding the currency and the
    monet value of a certain resource.
    """
    currency = StringField(read_only=True)
    amount = FloatField(read_only=True)
    breakdown = CompoundField(Breakdown, read_only=True)

    def __str__(self):
        return six.text_type(
            '<Price: currency={currency}, amount={amount}>'.format(
                currency=self.currency, amount=self.amount
            )
        )
