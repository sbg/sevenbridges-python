from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource


# noinspection PyProtectedMember
class Metadata(CompoundMutableDict, Resource):
    """
    File metadata resource.
    """
    _name = 'metadata'

    def __init__(self, **kwargs):
        super(Metadata, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            return self._parent._data[self._name][item]
        except KeyError:
            return None
