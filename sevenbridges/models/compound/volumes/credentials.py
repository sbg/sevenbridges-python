from sevenbridges.meta.resource import Resource
from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict


# noinspection PyProtectedMember
class VolumeCredentials(CompoundMutableDict, Resource):
    """
    Volume permissions resource.
    """
    _name = 'credentials'

    def __init__(self, **kwargs):
        super(VolumeCredentials, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            return self._parent._data[self._name][item]
        except KeyError:
            return None
