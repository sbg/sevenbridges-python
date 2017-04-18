import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class Breakdown(Resource):
    """
    Breakdown resource contains price breakdown by storage and computation.
    """
    storage = StringField(read_only=True)
    computation = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<Breakdown: storage={storage}, computation={computation}>'.format(
                storage=self.storage, computation=self.computation
            )
        )
