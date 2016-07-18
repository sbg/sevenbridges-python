import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class ImportDestination(Resource):
    """
    ImportDestination resource describes the location of the file
    imported on to SevenBridges platform or related product.
    """
    project = StringField(read_only=True)
    name = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<ImportDestination: project={project}, name={name}>'.format(
                project=self.project, name=self.name
            )
        )
