from sevenbridges.meta.resource import Resource


# noinspection PyUnresolvedReferences,PyProtectedMember
class BatchBy(Resource, dict):
    """
    Task batch by resource.
    """
    _name = 'batch_by'

    # noinspection PyMissingConstructor
    def __init__(self, **kwargs):
        self.parent = kwargs.pop('_parent')
        self.api = kwargs.pop('api')
        for k, v in kwargs.items():
            super().__setitem__(k, v)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
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
        return str(values)

    __str__ = __repr__

    def update(self, e=None, **f):
        other = {}
        if e:
            other.update(e, **f)
        else:
            other.update(**f)
        for k, v in other.items():
            if other[k] != self[k]:
                self[k] = other[k]

    def equals(self, other):
        if not type(other) == type(self):
            return False
        return (
            self is other or
            self._parent._data[self._name] == other._parent._data[self._name]
        )
