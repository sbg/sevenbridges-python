import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class Breakdown(Resource):
    """
    Breakdown resource contains price breakdown by storage and computation.
    """
    storage = StringField(read_only=True)
    computation = StringField(read_only=True)
    data_transfer = StringField(read_only=True)

    def __str__(self):
        if self.data_transfer:
            return six.text_type(
                '<Breakdown: storage={storage}, computation={computation}, '
                'data_transfer={data_transfer}>'.format(
                    storage=self.storage, computation=self.computation,
                    data_transfer=self.data_transfer
                )
            )
        return six.text_type(
            '<Breakdown: storage={storage}, computation={computation}>'.format(
                storage=self.storage, computation=self.computation
            )
        )
