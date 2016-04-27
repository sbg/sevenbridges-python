import six

from sevenbridges.meta.resource import Resource
from sevenbridges.meta.fields import HrefField


class DownloadInfo(Resource):
    """
    Download info resource contains download url for the file.
    """
    url = HrefField()

    def __str__(self):
        return six.text_type('<DownloadInfo: url={url}>'.format(url=self.url))
