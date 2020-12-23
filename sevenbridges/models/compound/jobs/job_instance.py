from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField, CompoundField
from sevenbridges.models.compound.jobs.job_instance_disk import Disk


class Instance(Resource):
    """
    Instance resource contains information regarding the instance
    on which the job was executed.
    """
    id = StringField(read_only=True)
    type = StringField(read_only=True)
    provider = StringField(read_only=True)
    disk = CompoundField(Disk, read_only=True)

    def __str__(self):
        return (
            f'<Instance id={self.id}, type={self.type}, '
            f'provider={self.provider}>'
        )
