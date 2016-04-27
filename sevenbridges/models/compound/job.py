import six

from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.job_log import Log
from sevenbridges.models.compound.job_instance import Instance
from sevenbridges.meta.fields import StringField, DateTimeField, CompoundField


class Job(Resource):
    """
    Job resource contains information for a single executed node
    in the analysis.
    """
    name = StringField(read_only=True)
    start_time = DateTimeField(read_only=True)
    end_time = DateTimeField(read_only=True)
    status = StringField(read_only=True)
    command_line = StringField(read_only=True)
    instance = CompoundField(Instance, read_only=True)
    logs = CompoundField(Log, read_only=True)

    def __str__(self):
        return six.text_type(
            '<Job: name={name}, status={status}>'.format(
                name=self.name, status=self.status
            )
        )
