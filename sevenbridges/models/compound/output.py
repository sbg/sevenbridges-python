import six

from sevenbridges.meta.resource import Resource
from sevenbridges.models.file import File


class Output(Resource, dict):
    """
    Task Output
    """

    def __init__(self, **kwargs):
        self._dirty = {}
        self._compound_cache = {}
        for k, v in kwargs.items():
            if isinstance(v, dict) and 'class' in v and v['class'].lower() \
                    == 'file':
                _file = File(id=v['path'], api=self._API)
                self[k] = _file
            elif isinstance(v, list):
                self[k] = [item for item in v if
                           not isinstance(item, dict)]
                self[k].extend(
                    [File(id=item['path'], api=self._API) for item
                     in v if
                     isinstance(item, dict)])
            else:
                self[k] = v
        self._dirty = {}
        self._compound_cache['outputs'] = self

    def __str__(self):
        values = {}
        for k, v in self.items():
            values[k] = v
        return six.text_type(
            '<Outputs> {}'.format(six.text_type(values)
                                  )
        )
