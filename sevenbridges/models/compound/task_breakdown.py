import six
from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.price import Price
from sevenbridges.meta.fields import (
    StringField, HrefField, CompoundField, DateTimeField
)


class TaskBreakdown(Resource):
    """
    Task breakdown resource contains information regarding
    billing group analysis breakdown costs.
    """
    href = HrefField()
    runner_username = StringField(read_only=True)
    time_started = DateTimeField(read_only=True)
    time_finished = DateTimeField(read_only=True)
    task_cost = CompoundField(Price, read_only=True)

    def __str__(self):
        return six.text_type('<TaskBreakdown:'
                             ' href={href}>'.format(href=self.href))
