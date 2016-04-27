import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import IntegerField, StringField


class ExecutionStatus(Resource):
    """
    Task execution status resource.
    Contains information about the number of completed task steps,
    total number of task steps and current execution message. In case
    of a batch task it also contains the number of queued, running, completed,
    failed and aborted tasks.
    """
    steps_completed = IntegerField(read_only=True)
    steps_total = IntegerField(read_only=True)
    message = StringField(read_only=True)
    queued = IntegerField(read_only=True)
    running = IntegerField(read_only=True)
    completed = IntegerField(read_only=True)
    failed = IntegerField(read_only=True)
    aborted = IntegerField(read_only=True)

    def __str__(self):
        return six.text_type('<ExecutionStatus>')
