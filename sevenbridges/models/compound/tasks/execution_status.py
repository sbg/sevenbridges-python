import six

from sevenbridges.meta.fields import IntegerField, StringField, BooleanField
from sevenbridges.meta.resource import Resource


class ExecutionStatus(Resource):
    """
    Task execution status resource.

    Contains information about the number of completed task steps,
    total number of task steps, current execution message and information
    regarding computation limits.

    In case of a batch task it also contains the number of queued, running,
    completed, failed and aborted tasks.
    """
    steps_completed = IntegerField(read_only=True)
    steps_total = IntegerField(read_only=True)
    message = StringField(read_only=True)
    message_code = StringField(read_only=True)
    queued = IntegerField(read_only=True)
    running = IntegerField(read_only=True)
    completed = IntegerField(read_only=True)
    failed = IntegerField(read_only=True)
    aborted = IntegerField(read_only=True)
    system_limit = BooleanField(read_only=True)
    account_limit = BooleanField(read_only=True)
    instance_init = BooleanField(read_only=True)
    queued_duration = IntegerField(read_only=True)
    running_duration = IntegerField(read_only=True)
    execution_duration = IntegerField(read_only=True)
    duration = IntegerField(read_only=True)

    def __str__(self):
        return six.text_type('<ExecutionStatus>')
