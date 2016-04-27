import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import BooleanField


class Permissions(Resource):
    """
    Permissions resource contains member permissions in regards to the project.
    """
    write = BooleanField()
    read = BooleanField()
    copy = BooleanField()
    execute = BooleanField()
    admin = BooleanField()

    def __str__(self):
        return six.text_type(
            '<Permissions: write={write}, read={read}, copy={copy},'
            ' execute={execute}, admin={admin}>'.format(
                write=self.write, read=self.read, copy=self.copy,
                execute=self.execute, admin=self.admin
            )
        )
