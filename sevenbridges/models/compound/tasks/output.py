from sevenbridges.errors import ReadOnlyPropertyError
from sevenbridges.meta.comp_mutable_dict import CompoundMutableDict
from sevenbridges.meta.resource import Resource
from sevenbridges.models.file import File


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
            inputs = self._parent._data[self._name][item]
            if isinstance(inputs, dict) and 'class' in inputs:
                if inputs['class'].lower() == 'file':
                    return File(id=inputs['path'], api=self._api)
            elif isinstance(inputs, list):
                items = [File(id=item['path'], api=self._api)
                         if isinstance(item, dict) else item
                         for item in inputs
                         ]
                return items
            else:
                return inputs
        except:
            return None

    def __setitem__(self, key, value):
        raise ReadOnlyPropertyError('Can not modify read only properties.')
