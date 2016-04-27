import re
import six

from sevenbridges.errors import SbgError
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import StringField
from sevenbridges.models.file import File


class Log(Resource):
    """
    Logs resource contains a url towards a file that contains
    execution logs for the job that executed.
    """
    _stderr = StringField(name='stderr', read_only=True)

    @property
    def stderr(self):
        if self._stderr is None:
            return None
        match = re.match(r'.*files/(.*)/.*', self._stderr)
        if match:
            file_id = match.groups()[0]
            return File(id=file_id, api=self._api)
        else:
            raise SbgError('Unable to fetch stderr file!')

    def __str__(self):
        return six.text_type(
            '<Logs: stderr={stderr}>'.format(stderr=self.stderr)
        )
