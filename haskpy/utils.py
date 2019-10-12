import functools


def singleton(C):
    return C()


def constructor(f):

    def wrapper(Cls):

        @functools.wraps(f)
        def _constructor(*args, **kwargs):
            return f(Cls, *args, **kwargs)

        return _constructor

    return wrapper
