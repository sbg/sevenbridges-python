import functools
import inspect


class AdvanceAccessHeader:
    key = 'X-Sbg-Advance-Access'
    value = 'Advance'


class advance_access(object):
    def __init__(self, obj=None):
        """
        Advance access context manger/decorator. Sets X-Sbg-Advance-Access
        header to the request object in order to access Seven Bridges
        advance access API features.
        :param obj: api instance or decorated function
        """
        self.obj = obj

    def __enter__(self):
        self.obj.headers.update({
            AdvanceAccessHeader.key: AdvanceAccessHeader.value
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if AdvanceAccessHeader.key in self.obj.headers:
            del self.obj.headers[AdvanceAccessHeader.key]

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(cls, *args, **kwargs):
            api = kwargs.get('api', None)
            if inspect.ismethod(f):
                # If its instance method
                api = api if api else cls._api
            else:
                # If its a classmethod
                api = api if api else cls._API
            with self.__class__(api):
                return f(cls, *args, **kwargs)

        return wrapper
