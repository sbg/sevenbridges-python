import six

from sevenbridges.errors import PaginationError
from sevenbridges.models.link import Link


class Collection(list):
    """
    Wrapper for SevenBridges pageable resources.
    Among the actual collection items it contains information regarding
    the total number of entries available in on the server and resource href.
    """

    resource = None

    def __init__(self, resource, href, total, items, links, api):
        super(Collection, self).__init__(items)
        self.resource = resource
        self.href = href
        self.links = links
        self._items = items
        self._total = total
        self._api = api

    @property
    def total(self):
        return int(self._total)

    def all(self):
        """
        Fetches all available items.
        :return: Collection object.
        """
        page = self._load(self.href)
        while True:
            try:
                for item in page._items:
                    yield item
                page = page.next_page()
            except PaginationError:
                break

    def _load(self, url):
        if self.resource is None:
            raise NotImplemented('Undefined collection resource.')
        else:
            response = self._api.get(url, append_base=False)
            data = response.json()
            total = response.headers['x-total-matching-query']
            items = [self.resource(api=self._api, **group) for group in
                     data['items']]
            links = [Link(**link) for link in data['links']]
            href = data['href']
            return Collection(
                resource=self.resource, href=href, total=total,
                items=items, links=links, api=self._api
            )

    def next_page(self):
        """
        Fetches next result set.
        :return: Collection object.
        """
        for link in self.links:
            if link.rel.lower() == 'next':
                return self._load(link.href)
        raise PaginationError('No more entries.')

    def previous_page(self):
        """
        Fetches previous result set.
        :return: Collection object.
        """
        for link in self.links:
            if link.rel.lower() == 'prev':
                return self._load(link.href)
        raise PaginationError('No more entries.')

    def __repr__(self):
        return six.text_type(
            '<Collection: total={total}, available={items}>'.format(
                total=self.total, items=len(self._items)
            )
        )
