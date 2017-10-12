import logging

import six

from sevenbridges.http.client import client_info
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.enums import FeedbackType

logger = logging.getLogger(__name__)


class Actions(Resource):
    _URL = {
        'send_feedback': '/action/notifications/feedback',
        'bulk_copy': '/action/files/copy'
    }

    def __str__(self):
        return six.text_type('<Actions>')

    @classmethod
    def send_feedback(cls, type=FeedbackType.IDEA, referrer=None, text=None,
                      api=None):
        """
        Sends feedback to sevenbridges.
        :param type: FeedbackType wither IDEA, PROBLEM or THOUGHT.
        :param text: Feedback text.
        :param referrer: Feedback referrer.
        :param api: Api instance.
        """
        api = api if api else cls._API
        data = {'type': type,
                'text': text,
                'referrer': referrer if referrer else six.text_type(
                    client_info
                )}

        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Sending feedback', extra=extra)
        api.post(url=cls._URL['send_feedback'], data=data)

    @classmethod
    def bulk_copy_files(cls, files, destination_project, api=None):
        """
        Bulk copy of files.
        :param files: List containing files to be copied.
        :param destination_project: Destination project.
        :param api: Api instance.
        :return: MultiStatus copy result.
        """
        api = api if api else cls._API
        files = [Transform.to_file(file) for file in files]
        data = {
            'project': destination_project,
            'file_ids': files
        }
        extra = {
            'resource': cls.__name__,
            'query': data
        }
        logger.info('Performing bulk copy', extra=extra)
        return api.post(url=cls._URL['bulk_copy'], data=data).json()
