from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.enums import FeedbackType


class Actions(Resource):
    _URL = {
        'send_feedback': '/action/notifications/feedback',
        'bulk_copy': '/action/files/copy'
    }

    @classmethod
    def send_feedback(cls, type=FeedbackType.IDEA, text=None, api=None):
        """
        Sends feedback to sevenbridges.
        :param type: FeedbackType wither IDEA, PROBLEM or THOUGHT.
        :param text: Feedback text.
        :param api: Api instance.
        """
        api = api if api else cls._API
        data = {
            'type': type,
            'text': text,
        }
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
        return api.post(url=cls._URL['bulk_copy'], data=data).json()
