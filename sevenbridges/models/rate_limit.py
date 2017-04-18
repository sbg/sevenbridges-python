from sevenbridges.meta.fields import CompoundField
from sevenbridges.meta.resource import Resource
from sevenbridges.models.compound.limits.rate import Rate


class RateLimit(Resource):
    """
    Rate limit resource contains info regarding request and computation
    rate limits.
    """

    _URL = {
        'get': '/rate_limit'
    }
    rate = CompoundField(Rate, read_only=True)
    instance_limit = CompoundField(Rate, read_only=True)

    @classmethod
    def get(cls, id=None, api=None):
        api = api if api else cls._API
        resource = api.get(url=cls._URL['get']).json()
        return cls(api=api, **resource)
