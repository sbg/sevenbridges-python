import six

from sevenbridges.meta.fields import StringField
from sevenbridges.meta.resource import Resource


class VolumePrefix(Resource):
    """
    Volume prefix resource contains information about volume prefixes
    """
    href = StringField(read_only=True)
    prefix = StringField(read_only=True)
    volume = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<VolumePrefix: prefix={prefix}>'.format(
                prefix=self.prefix
            )
        )
