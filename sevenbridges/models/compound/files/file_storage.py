import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField


class FileStorage(Resource):
    """
    File storage resource contains information about the storage location
    of the file if the file is imported on or exported to an external volume.
    """
    type = StringField(read_only=True)
    volume = StringField(read_only=True)
    location = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<FileStorage: type={type}, volume={volume}>'.format(
                type=self.type, volume=self.volume
            )
        )
