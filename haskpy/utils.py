import functools
import inspect
import attr


def singleton(C):
    return C()


def constructor(f):

    def wrapper(Cls):

        @functools.wraps(f)
        def _constructor(*args, **kwargs):
            return f(Cls, *args, **kwargs)

        return _constructor

    return wrapper


def curry(f):
    # toolz Python package has curry function but it's unusable. The main
    # problem being you don't get errors when doing something wrong but instead
    # some really weird results.
    #
    # For instance, when a type error is raised nested inside the function, it
    # will be silenced: https://github.com/pytoolz/toolz/issues/471. That is,
    # the following doesn't raise an exception but returns a weird function:
    #
    # >>> toolz.curry(lambda *args, **kwargs: (lambda x, y: x - y)(*args, **kwargs))(5, 3, 1)
    #
    # In HaskPy, this resulted in the following example to not raise an error
    # but give weird results:
    #
    # >>> haskpy.compose(pyhask.map, pyhask.map)(
    # ...     lambda x: 100*x,
    # ...     haskpy.Just(pyhask.List(1,2,3)),
    # ...     "these extra arguments",
    # ...     "should cause an error"
    # ... )
    #
    # Also, this should raise an error:
    #
    # >>>  toolz.curry(lambda *args, **kwargs: (lambda x, y: x + y)(*args, **kwargs))(1, "h")
    #
    # In Haskpy, this corresponds to a missing error from:
    #
    # >>> haskpy.Just(pyhask.List(1,2,3)).map(lambda x: x+1)
    #
    # Also, toolz.curry seems overly complex and bloated. I have no idea what
    # they are actually doing with all that code and magic.. At least for my
    # purposes, currying is very simple as the implementation below shows.
    #
    # So, let's implement our own simple curry function correctly.

    if not callable(f):
        raise TypeError("'{}' object is not callable".format(type(f).__name__))

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        fp = functools.partial(f, *args, **kwargs)
        try:
            spec = inspect.getfullargspec(fp)
        except TypeError:
            # This exception is raised when an invalid arguments (positional or
            # keyword) are passed. To make the exception traceback simpler,
            # call the original function directly and don't use the partial.
            # Also, call the function outside this try-except so these
            # exceptions won't show up in the traceback.
            use_partial = False
        else:
            use_partial = True
            n_args = len(spec.args) - (
                0 if spec.defaults is None else
                len(spec.defaults)
            )
            # Positional required arguments may get into required keyword
            # argument position if some positional arguments before them are
            # given as keyword arguments. For instance:
            #
            # curry(lambda x, y: x - y)(x=5)
            #
            # Now, y becomes a keyword argument but it's still required as it
            # doesn't have any default value. Handle this by looking at
            # kwonlyargs that don't have a value in kwonlydefaults.
            defaults = (
                set() if spec.kwonlydefaults is None else
                set(spec.kwonlydefaults.keys())
            )
            kws = set(spec.kwonlyargs)
            n_kw = len(kws.difference(defaults))
        return (
            # 1) Invalid arguments, use the original function
            f(*args, **kwargs) if not use_partial else
            # 2) No arguments missing, evaluate the function
            fp()               if n_args + n_kw == 0 else
            # 3) Function is still waiting for some required arguments, use the
            # partial function (curried)
            curry(fp)
        )

    return wrapped


@attr.s(frozen=True, repr=False)
class function():


    f = attr.ib(
        converter=curry,
        validator=lambda _, __, value: callable(value),
    )


    @classmethod
    def pure(cls, x):
        return cls(lambda _: x)


    def __call__(self, *args, **kwargs):
        # Forward the call to the underlying real Function class.
        #
        # In order to avoid circular imports, import Function here inside this
        # function.
        from haskpy.types._function import Function as F
        return F.__call__(self, *args, **kwargs)


    def __getattr__(self, name):
        # Forward the attribute query to the underlying real Function class.
        #
        # In order to avoid circular imports, import Function here inside this
        # function.
        from haskpy.types._function import Function as F
        return getattr(F(self.f), name)


    def __get__(self, obj, objtype):
        """Support instance methods.

        See: https://stackoverflow.com/a/3296318

        """
        return function(functools.partial(self.__call__, obj))


    def __repr__(self):
        return repr(self.f)


@function
def compose(g, f):
    return function(f).map(g)
