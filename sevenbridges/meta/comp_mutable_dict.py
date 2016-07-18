import six


# noinspection PyProtectedMember,PyUnresolvedReferences
class CompoundMutableDict(dict):
    """
    Resource used for mutable compound dictionaries.
    """

    def __init__(self, **kwargs):
        self._parent = kwargs.pop('parent')
        self._api = kwargs.pop('api')
        for k, v in kwargs.items():
            super(CompoundMutableDict, self).__setitem__(k, v)

    def __setitem__(self, key, value):
        super(CompoundMutableDict, self).__setitem__(key, value)
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
        same = self._parent._data[self._name] == other.parent._data[self._name]
        return type(self) == type(other) and same
