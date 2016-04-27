import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import DateTimeField


class InvoicePeriod(Resource):
    """
    Invoice period resource contains datetime information about the invoice.
    It has from and to fields which represent the interval period for this
    invoice.
    """
    from_ = DateTimeField(name='from', read_only=True)
    to = DateTimeField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<InvoicePeriod: from={from_}, to={to}>'.format(
                from_=self.from_, to=self.to
            )
        )
