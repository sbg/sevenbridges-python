import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import CompoundField
from sevenbridges.models.compound.error import Error


class BulkRecord(Resource):
    error = CompoundField(cls=Error)
    resource = CompoundField(cls=Resource)

    def __str__(self):
        return six.text_type('<BulkRecord>')

    @property
    def valid(self):
        return self.error is None
