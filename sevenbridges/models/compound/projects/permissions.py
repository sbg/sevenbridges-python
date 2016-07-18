from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource


# noinspection PyProtectedMember
class Permissions(CompoundMutableDict, Resource):
    """
    Members permissions resource.
    """
    _name = 'permissions'

    def __init__(self, **kwargs):
        super(Permissions, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            return self._parent._data[self._name][item]
        except KeyError:
            return None
