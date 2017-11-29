import six

from sevenbridges.meta.fields import StringField
from sevenbridges.meta.resource import Resource


class VolumeFile(Resource):
    """
    VolumeFile resource describes the location of the file
    on the external volume.
    """
    volume = StringField(read_only=True)
    location = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<VolumeFile: volume={volume}, location={location}>'.format(
                volume=self.volume, location=self.location
            )
        )

    def __eq__(self, other):
        if not hasattr(other, '__class__'):
            return False
        if not self.__class__ == other.__class__:
            return False
        return self is other or self.location == other.location

    def __ne__(self, other):
        return not self.__eq__(other)
