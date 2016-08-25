# noinspection PyProtectedMember
from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource


class Settings(CompoundMutableDict, Resource):
    """
    Project settings resource.
    """
    _name = 'settings'

    def __init__(self, **kwargs):
        super(Settings, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            return self._parent._data[self._name][item]
        except KeyError:
            return None
