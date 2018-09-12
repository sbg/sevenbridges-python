from sevenbridges.errors import ReadOnlyPropertyError
from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.tasks import map_input_output


# noinspection PyProtectedMember
class Output(CompoundMutableDict, Resource):
    """
    Task output resource.
    """
    _name = 'outputs'

    def __init__(self, **kwargs):
        super(Output, self).__init__(**kwargs)

    def __getitem__(self, item):
        try:
            output = self._parent._data[self._name][item]
            return map_input_output(output, self._api)
        except Exception:
            return None

    def __setitem__(self, key, value):
        raise ReadOnlyPropertyError('Can not modify read only properties.')
