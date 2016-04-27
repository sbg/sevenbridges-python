import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField, BasicListField


class BatchBy(Resource):
    """
    Batch by tells the API what is the criteria
    for batching. It can be either item or criteria.
    """
    type = StringField(read_only=False)
    criteria = BasicListField(read_only=False)

    @staticmethod
    def __str__():
        return six.text_type('<Batch by>')
