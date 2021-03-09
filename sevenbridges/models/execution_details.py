from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.jobs.job import Job
from sevenbridges.meta.fields import (
    HrefField, DateTimeField, StringField, CompoundListField
)


class ExecutionDetails(Resource):
    """
    Task execution details.
    """
    href = HrefField(read_only=True)
    start_time = DateTimeField(read_only=True)
    end_time = DateTimeField(read_only=True)
    status = StringField(read_only=True)
    message = StringField(read_only=True)
    jobs = CompoundListField(Job, read_only=True)

    def __str__(self):
        return '<Execution Details>'
