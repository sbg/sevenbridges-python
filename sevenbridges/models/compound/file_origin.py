import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class FileOrigin(Resource):
    """
    File origin resource contains information about origin of a file.
    Among others it contains information about the task if the file
    was produced during executions of a analysis.
    """
    task = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<FileOrigin: task={task}>'.format(task=self.task)
        )
