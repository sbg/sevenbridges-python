import logging


logger = logging.getLogger(__name__)


class DataContainer(object):
    """
    Utility for fetching data from the API server using,
    resource identifier or href.
    """

    def __init__(self, urls, api):
        self.data = {}
        self._URL = urls
        self.api = api
        self.fetched = False

    def fetch(self, item=None):

        logger.debug(
            'Property "%s" is not set, fetching resource from server', item
        ) if item else logger.debug(
            'Requested property is not set, fetching resource from server',
        )

        href = self.data.get('href', None)
        headers = dict(self.api.headers)

        if href is not None:
            self.data = self.api.get(
                href,
                headers=headers,
                append_base=False
            ).json()
            logger.debug('Resource fetched using the "href" property.')
        elif self._URL is not None and 'get' in self._URL:
            resource_id = self.data.get('id', None)
            if resource_id is None:
                logger.debug(
                    'Failed to fetch resource, "id" or "href" property '
                    'not set'
                )
                return
            self.data = self.api.get(
                self._URL['get'].format(id=resource_id),
                headers=headers,
                append_base=True
            ).json()
            logger.debug('Resource fetched using the id property.')
        else:
            logger.debug(
                'Skipping resource fetch, retrieval for this resource is '
                'not available.'
            )
            return
        self.fetched = True

    def __getitem__(self, item):
        if item not in self.data and not self.fetched:
            self.fetch(item=item)
        try:
            return self.data[item]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.data[key] = value
