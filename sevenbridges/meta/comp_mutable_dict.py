# noinspection PyProtectedMember,PyUnresolvedReferences
class CompoundMutableDict(dict):
    """
    Resource used for mutable compound dictionaries.
    """

    # noinspection PyMissingConstructor
    def __init__(self, **kwargs):
        self._parent = kwargs.pop('_parent')
        self._api = kwargs.pop('api')
        for k, v in kwargs.items():
            super().__setitem__(k, v)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self._name not in self._parent._dirty:
            self._parent._dirty.update({self._name: {}})
        if key in self._parent._data[self._name]:
            if self._parent._data[self._name][key] != value:
                self._parent._dirty[self._name][key] = value
                self._parent._data[self._name][key] = value
        else:
            self._parent._data[self._name][key] = value
            self._parent._dirty[self._name][key] = value

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

    def items(self):
        values = []
        for k in self.keys():
            values.append((k, self[k]))
        return values

    def equals(self, other):
        if not type(other) == type(self):
            return False
        return (
            self is other or
            self._parent._data[self._name] == other._parent._data[self._name]
        )
