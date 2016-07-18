import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class JobDocker(Resource):
    """
    JobDocker resource contains information for a docker image that was
    used for execution of a single job.
    """
    checksum = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<Docker: checksum={checksum}'.format(checksum=self.checksum)
        )
