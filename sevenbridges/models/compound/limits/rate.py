import six

from sevenbridges.meta.fields import IntegerField, DateTimeField
from sevenbridges.meta.resource import Resource


class Rate(Resource):
    """
    Rate resource.
    """
    limit = IntegerField(read_only=True)
    remaining = IntegerField(read_only=True)
    reset = DateTimeField()

    def __str__(self):
        return six.text_type(
            '<Rate: limit={limit}, remaining={rem}>'
            .format(limit=self.limit, rem=self.remaining)
        )
