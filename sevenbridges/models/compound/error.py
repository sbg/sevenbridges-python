import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import IntegerField, StringField


class Error(Resource):
    """
    Error resource describes the error that happened and provides
    http status, custom codes and messages as well as the link to
    online resources.
    """
    status = IntegerField(read_only=True)
    code = IntegerField(read_only=True)
    message = StringField(read_only=True)
    more_info = StringField(read_only=True)

    def __str__(self):
        return six.text_type(
            '<Error: status={status}, code={code}>'.format(
                status=self.status, code=self.code
            )
        )
