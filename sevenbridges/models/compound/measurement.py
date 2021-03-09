from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField, FloatField


class Measurement(Resource):
    """
    Measurement resource contains an information regarding the size and the
    unit of a certain resource.
    """
    size = FloatField(read_only=True)
    unit = StringField(read_only=True)

    def __str__(self):
        return f'<Measurement size={self.size}, unit={self.unit}>'
