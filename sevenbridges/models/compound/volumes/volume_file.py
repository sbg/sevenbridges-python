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
        return f'<VolumeFile: volume={self.volume}, location={self.location}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.location == other.location
