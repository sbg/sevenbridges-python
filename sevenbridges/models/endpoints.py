import logging

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import HrefField

logger = logging.getLogger(__name__)


class Endpoints(Resource):
    """
    Central resource for managing Endpoints.
    """
    _URL = {
        'get': '/'
    }

    rate_limit_url = HrefField(read_only=True)
    user_url = HrefField(read_only=True)
    users_url = HrefField(read_only=True)
    billing_url = HrefField(read_only=True)
    projects_url = HrefField(read_only=True)
    files_url = HrefField(read_only=True)
    tasks_url = HrefField(read_only=True)
    apps_url = HrefField(read_only=True)
    action_url = HrefField(read_only=True)
    upload_url = HrefField(read_only=True)

    @classmethod
    def get(cls, api=None, **kwargs):
        """
        Get api links.
        :param api: Api instance.
        :return: Endpoints object.
        """
        api = api if api else cls._API
        extra = {
            'resource': cls.__name__,
            'query': {}
        }
        logger.info('Getting resources', extra=extra)
        endpoints = api.get(url=cls._URL['get']).json()
        return Endpoints(api=api, **endpoints)

    def __str__(self):
        return '<Endpoints>'
