from sevenbridges.meta.fields import CompoundField
from sevenbridges.meta.resource import Resource
from sevenbridges.models.file import File
from sevenbridges.models.compound.error import Error


class FileImportResult(Resource):
    """
    File result resource used for actions that may return resource or error out
    """
    error = CompoundField(Error, read_only=True)
    resource = CompoundField(File, read_only=True)

    def __str__(self):
        return f'{str(self.error) if self.error else str(self.resource)}'
