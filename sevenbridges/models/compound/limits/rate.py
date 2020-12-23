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
        return f'<Rate: limit={self.limit}, remaining={self.remaining}>'
