import functools
import inspect
import attr


def singleton(C):
    return C()


def update_argspec(name, spec, args, kwargs):

    raise NotImplementedError()

    # TODO: Instead of running getfullargspec after every partial evaluation,
    # it might be faster to use the existing argspec and update that based on
    # args and kwargs. However, the speed gains might be quite small and one
    # needs to be very careful to implement exactly the same logic that Python
    # itself uses. It is possible that this logic changes from one Python
    # version to another, so it might become a maintenance nightmare. Still,
    # perhaps worth at least checking.
    #
    # Below is just some sketching.

    no_varargs = spec.varargs is None

    nargs_takes = len(spec.args)
    nargs_given = len(args)
    if no_varargs and nargs_given > nargs_takes:
        raise TypeError(
            "{name} takes {takes} positional argument but {given} were given"
            .format(
                name=name,
                takes=nargs_takes,
                given=nargs_given,
            )
        )

    # FIXME: Handle kw too
    new_args = spec.args[nargs_given:]

    # FIXME:
    new_defaults = spec.defaults
    new_kwonlyargs = spec.kwonlyargs
    new_kwonlydefaults = spec.kwonlydefaults

    return inspect.FullArgSpec(
        args=new_args,
        varargs=spec.varargs,
        varkw=spec.varkw,
        defaults=new_defaults,
        kwonlyargs=new_kwonlyargs,
        kwonlydefaults=new_kwonlydefaults,
        # FIXME: What to do with this?
        annotations=spec.annotations,
    )
    pass


def count_required_arguments(argspec):

    # Positional arguments without defaults provided
    n_args = len(argspec.args) - (
        0 if argspec.defaults is None else
        len(argspec.defaults)
    )

    # Positional required arguments may get into required keyword
    # argument position if some positional arguments before them are
    # given as keyword arguments. For instance:
    #
    #   curry(lambda x, y: x - y)(x=5)
    #
    # Now, y becomes a keyword argument but it's still required as it
    # doesn't have any default value. Handle this by looking at
    # kwonlyargs that don't have a value in kwonlydefaults.
    defaults = (
        set() if argspec.kwonlydefaults is None else
        set(argspec.kwonlydefaults.keys())
    )
    kws = set(argspec.kwonlyargs)
    n_kw = len(kws.difference(defaults))

    return n_args + n_kw


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

        try:
            # Handle a normal fully evaluated function fast. We want to get
            # full argspec only if necessary as that takes quite a bit of time
            # compared to just evaluating a function.
            return f(*args, **kwargs)
        except TypeError:
            fp = functools.partial(f, *args, **kwargs)
            try:
                # This is quite slow.. It's about 1000x slower than just
                # normally calling a function. See:
                # https://bugs.python.org/issue37010. Any way to speed it up,
                # do something else or avoid it?
                #
                # TODO: Perhaps worth considering if it would speed things up
                # if the full argspec is propagated recursively to curry for
                # partially evaluated functions. That way, they can just update
                # the existing argspec based on args and kwargs instead of
                # finding it from scratch. See update_argspec above. Then,
                # curry function would take argspec as an optional argument.
                spec = inspect.getfullargspec(fp)
            except TypeError:
                # This exception is raised when an invalid arguments (positional or
                # keyword) are passed. To make the exception traceback simpler,
                # call the original function directly and don't use the partial.
                # Also, call the function outside this try-except so these
                # exceptions won't show up in the traceback.
                raise_error = True
            else:
                raise_error = False

            # Invalid arguments, raise the original exception
            if raise_error:
                raise

            n_required = count_required_arguments(spec)

            # If no arguments missing, evaluate the function
            return (
                # 1) No arguments missing, evaluate the function
                fp() if n_required == 0 else
                # 2) Function is still waiting for some required arguments, use the
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
