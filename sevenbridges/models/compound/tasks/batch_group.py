import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField, DictField


class BatchGroup(Resource):
    """
    Batch group for a batch task.
    Represents the group that is assigned to the child task
    from the batching criteria that was used when the task was started.
    """
    value = StringField(read_only=True)
    fields = DictField(read_only=True)

    @staticmethod
    def __str__():
        return six.text_type('<Batch group>')
