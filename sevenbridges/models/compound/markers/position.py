from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource


class MarkerPosition(CompoundMutableDict, Resource):
    """
    Marker position resource
    """
    _name = 'position'

    def __init__(self, **kwargs):
        super(MarkerPosition, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            return self._parent._data[self._name][item]
        except KeyError:
            return None
