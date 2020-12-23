from sevenbridges.meta.fields import StringField, DictField
from sevenbridges.meta.resource import Resource


class VolumeObject(Resource):
    """
    Volume object resource contains information about single
    file (object) entry in a specific volume.
    """
    href = StringField(read_only=True)
    location = StringField(read_only=True)
    volume = StringField(read_only=True)
    type = StringField(read_only=True)
    metadata = DictField(read_only=True)

    def __str__(self):
        return f'<VolumeObject: location={self.location}>'
