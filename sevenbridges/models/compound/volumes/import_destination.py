from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class ImportDestination(Resource):
    """
    ImportDestination resource describes the location of the file
    imported on to SevenBridges platform or related product.
    """
    project = StringField(read_only=True)
    parent = StringField(read_only=True)
    name = StringField(read_only=True)

    def __str__(self):
        return f'<ImportDestination: project={self.project}, name={self.name}>'
