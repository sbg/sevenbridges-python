from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource


class MarkerPosition(CompoundMutableDict, Resource):
    """
    Marker position resource
    """
    _name = 'position'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getitem__(self, item):
        try:
            # noinspection PyProtectedMember
            return self._parent._data[self._name][item]
        except KeyError:
            return None
