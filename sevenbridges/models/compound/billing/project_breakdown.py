from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.price import Price
from sevenbridges.models.compound.billing.task_breakdown import TaskBreakdown
from sevenbridges.meta.fields import (
    HrefField, CompoundField, CompoundListField
)


class ProjectBreakdown(Resource):
    """
    Project breakdown resource contains information regarding
    billing group project breakdown costs.
    """
    href = HrefField(read_only=True)
    analysis_spending = CompoundField(Price, read_only=True)
    task_breakdown = CompoundListField(TaskBreakdown, read_only=True)

    def __str__(self):
        return f'<ProjectBreakdown: href={self.href}>'
