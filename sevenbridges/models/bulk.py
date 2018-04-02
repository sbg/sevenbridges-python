import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import CompoundField
from sevenbridges.models.compound.error import Error


class BulkRecord(Resource):
    error = CompoundField(cls=Error)
    resource = CompoundField(cls=Resource)

    def __str__(self):
        return six.text_type('<BulkRecord>')

    @property
    def valid(self):
        return self.error is None

    @classmethod
    def parse_records(cls, response, api=None):
        api = api or cls._API
        records = []
        data = response.json()
        for item in data.get('items', []):
            record = cls(api=api)
            if 'error' in item:
                record.error = item['error']
            if 'resource' in item:
                record.resource = item['resource']
            records.append(record)
        return records
