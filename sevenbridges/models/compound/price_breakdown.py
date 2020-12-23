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
            return (
                f'<Breakdown: storage={self.storage}, '
                f'computation={self.computation}, '
                f'data_transfer={self.data_transfer}>'
            )
        return (
            f'<Breakdown: storage={self.storage}, '
            f'computation={self.computation}>'
        )
