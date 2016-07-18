import re

from sevenbridges.errors import SbgError, ReadOnlyPropertyError
from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource
from sevenbridges.models.file import File


# noinspection PyProtectedMember
class Logs(CompoundMutableDict, Resource):
    """
    Task output resource.
    """
    _name = 'logs'

    def __init__(self, **kwargs):
        super(Logs, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            log = self._parent._data[self._name][item]
            match = re.match(r'.*files/(.*)/.*', log)
            if match:
                file_id = match.groups()[0]
                return File(id=file_id, api=self._api)
            else:
                raise SbgError('Unable to fetch {} log file!'.format(item))
        except:
            return None

    def __setitem__(self, key, value):
        raise ReadOnlyPropertyError('Can not modify read only properties.')
