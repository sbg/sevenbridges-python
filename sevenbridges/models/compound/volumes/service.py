from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict

from sevenbridges.meta.resource import Resource


class VolumeService(CompoundMutableDict, Resource):
    """
    Volume Service resource. Contains information about external
    storage provider.
    """
    _name = 'service'

    def __init__(self, **kwargs):
        super(VolumeService, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            return self._parent._data[self._name][item]
        except KeyError:
            return None
