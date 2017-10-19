import itertools

FILTERS = ('my_oct', 'my_hex', 'my_bin')
METHODS = ('LAMBDA', 'LAMBDA2', 'DEF', 'MIMIC', 'STATIC', 'BUILTIN')


class Mimic(object):
    """Mimics class I want need to use.
    Initialization take an argument and uses it in method.
    """
    def __init__(self, func):
        self.func = func

    def method(self, v):
        return self.func(v)


class MyFilters(object):
    """Just using the class as a namespace."""
    @staticmethod
    def my_oct(x):
        return oct(x)

    @staticmethod
    def my_hex(x):
        return hex(x)

    @staticmethod
    def my_bin(x):
        return bin(x)


def make_filters(filter_names, method):
    if method == 'LAMBDA':
        # Give me lambdas to the built in functions
        filters = {_: lambda x, f=__builtins__[ _[3:]]: f(x)
                   for _ in filter_names}
    elif method == 'LAMBDA2':
        filters = {_: (lambda x, f=_[3:]: __builtins__[f](x))
                   for _ in filter_names}
    elif method == 'DEF':
        filters = {}
        for name in filter_names:
            def a_filter(x, f=__builtins__[name[3:]]):
                return f(x)
            filters[name] = a_filter
    elif method == 'BUILTIN':
        filters = {name: __builtins__[name[3:]] for name in filter_names}
    elif method == 'STATIC':
        filters = {name: getattr(MyFilters, name) for name in filter_names}
    elif method == 'MIMIC':
        filters = {name: (lambda x, f=Mimic(__builtins__[name[3:]]): f.method(x))
                   for name in filter_names}
    return filters
