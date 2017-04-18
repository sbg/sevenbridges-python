import logging
import six

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

    rate_limit_url = HrefField()
    user_url = HrefField()
    users_url = HrefField()
    billing_url = HrefField()
    projects_url = HrefField()
    files_url = HrefField()
    tasks_url = HrefField()
    apps_url = HrefField()
    action_url = HrefField()
    upload_url = HrefField()

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

    @staticmethod
    def __str__():
        return six.text_type('<Endpoints>')
