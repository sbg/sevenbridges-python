import six

from sevenbridges.meta.resource import Resource


# noinspection PyUnresolvedReferences,PyProtectedMember
class BatchBy(Resource, dict):
    """
    Task batch by resource.
    """
    _name = 'batch_by'

    def __init__(self, **kwargs):
        self.parent = kwargs.pop('parent')
        self.api = kwargs.pop('api')
        for k, v in kwargs.items():
            super(BatchBy, self).__setitem__(k, v)

    def __setitem__(self, key, value):
        super(BatchBy, self).__setitem__(key, value)
        self.parent._data[self._name][key] = value
        if self._name not in self.parent._dirty:
            self.parent._dirty.update({self._name: {}})
        self.parent._dirty[self._name][key] = value

    def __getitem__(self, item):
        try:
            return self.parent._data[self._name][item]
        except KeyError:
            return None

    def __repr__(self):
        values = {}
        for k, _ in self.items():
            values[k] = self[k]
        return six.text_type(values)

    __str__ = __repr__

    def update(self, E=None, **F):
        other = {}
        if E:
            other.update(E, **F)
        else:
            other.update(**F)
        for k, v in other.items():
            if other[k] != self[k]:
                self[k] = other[k]

    def equals(self, other):
        same = self.parent._data[self._name] == other.parent._data[self._name]
        return type(self) == type(other) and same
