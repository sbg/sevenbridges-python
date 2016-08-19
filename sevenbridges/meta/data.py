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

    def fetch(self):
        href = self.data.get('href', None)
        if href is not None:
            self.data = self.api.get(self.data['href'],
                                     append_base=False).json()
        else:
            resource_id = self.data.get('id', None)
            if resource_id is None:
                return
            self.data = self.api.get(self._URL['get'].format(id=resource_id),
                                     append_base=True).json()
        self.fetched = True

    def __getitem__(self, item):
        if item not in self.data and not self.fetched:
            self.fetch()
        try:
            return self.data[item]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.data[key] = value
