import functools
import inspect


class AdvanceAccessHeader:
    key = 'X-Sbg-Advance-Access'
    value = 'Advance'


class advance_access(object):
    def __init__(self, obj=None):
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
                api = api if api else cls._api
            else:
                api = api if api else cls._API
            with self.__class__(api):
                return f(cls, *args, **kwargs)

        return wrapper
