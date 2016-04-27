from sevenbridges.meta.resource import Resource


class Metadata(Resource, dict):
    """
    File metadata resource.
    """
    def __init__(self, **kwargs):
        self._dirty = {}
        self._compound_cache = {}
        for k, v in kwargs.items():
            self[k] = v
        self._dirty = {}
        self._compound_cache['metadata'] = self

    def __setitem__(self, key, value):
        self._dirty[key] = value
        super(Metadata, self).__setitem__(key, value)
