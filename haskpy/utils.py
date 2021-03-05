"""Utilities

.. autosummary::
   :toctree:

   immutable

"""
import functools
import inspect
import attr
import hypothesis.strategies as st


def immutable(maybe_cls=None, eq=False, repr=False, **kwargs):
    return attr.s(
        maybe_cls=maybe_cls,
        frozen=True,
        eq=eq,
        order=False,
        hash=False,
        str=False,
        repr=repr,
        **kwargs
    )


def singleton(C):
    return C()


class decorator():
    """Base class for various decorators"""

    def __init__(self, f):
        self.f = f
        self.__doc__ = f.__doc__
        self.__name__ = f.__name__
        self.__module__ = f.__module__
        self.__defaults__ = f.__defaults__
        self.__kwdefaults__ = f.__kwdefaults__
        self.__annotations__ = f.__annotations__
        return

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    @property
    def __code__(self):
        return self.f.__code__

    @property
    def __signature__(self):
        return inspect.signature(self.f)

    # The following properties are needed so that Sphinx recognizes (class)
    # methods. Note that these properties don't exist for normal functions.

    @property
    def __self__(self):
        return self.f.__self__

    @property
    def __func__(self):
        return self.f.__func__


class class_function(decorator):
    """Class method that isn't a method of the instances"""

    def __get__(self, obj, cls):
        if obj is None:
            return self.f.__get__(cls, type(cls))
        else:
            raise AttributeError(
                "'{0}' object has no attribute '{1}'".format(
                    cls.__name__,
                    self.f.__name__,
                )
            )


class class_property(decorator):
    """Class attribute that isn't an attribute of the instances

    To access the docstring, use ``__dict__`` as
    ``SomeClass.__dict__["some_attribute"].__doc__``

    """

    def __get__(self, obj, cls):
        if obj is None:
            return self.f.__get__(obj, cls)(cls)
        else:
            raise AttributeError(
                "'{0}' object has no attribute '{1}'".format(
                    cls.__name__,
                    self.f.__name__,
                )
            )


class abstract_function(decorator):
    """Function that has no implementation yet"""

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(
            "'{0}' function is abstract".format(self.f.__name__)
        )

    def __get__(self, obj, cls):
        return abstract_function(self.f.__get__(obj, cls))

    @property
    def __code__(self):
        return self.f.__code__

    @property
    def __signature__(self):
        return inspect.signature(self.f)


class abstract_property(decorator):
    """Property that has no implementation yet

    To access the property ``abstract_property`` object without raising
    ``NotImplementedError``, use ``__dict__``. For instance, to access the
    docstring:

    .. code-block:: python

        class Foo():

            @abstract_property
            def bar(self):
                '''My docstring'''

        Foo.__dict__["bar"].__doc__
        isinstance(Foo.__dict__["bar"], abstract_property)

    """

    def __get__(self, obj, cls):
        self.f.__get__(obj, cls)
        raise NotImplementedError(
            "'{0}' attribute of type object '{1}' is abstract".format(
                self.f.__name__,
                cls.__name__,
            )
            if obj is None else
            "'{0}' attribute of object '{1}' is abstract".format(
                self.f.__name__,
                cls.__name__,
            )
        )


def abstract_class_property(f):
    return abstract_property(class_function(f))


def abstract_class_function(f):
    # Wrap the result gain with class_function so that we can recognize the
    # result as a class function when building the documentation.. A bit ugly
    # hack.. Probably there's a better way..
    return abstract_function(class_function(f))


@immutable
class nonexisting_function():
    """Mark method non-existing

    This is a workaround for Python forcefully creating some methods. One
    cannot create objects that don't have ``__eq__``, ``__ge__``, ``__gt__``
    and many other methods. They are there and it's not possible to delete
    them. With this wrapper you can override those methods so that they won't
    show up in ``__dir__`` listing and if accessed in any way,
    ``AttributeError`` is raised. Note that it just hides the methods, one can
    still access them as ``object.__getattribute__(obj, "__eq__")``.

    """

    method = attr.ib()
    cls = attr.ib(default=None)

    def __call__(self, *args, **kwargs):
        name = self.method.__name__
        # The method doesn't exist
        raise TypeError(
            "No {0} function".format(name)
            if self.cls is None else
            "Class {0} has no {1} method".format(self.cls.__name__, name)
        )

    def __get__(self, obj, objtype):
        # Bind the method to a class
        return nonexisting_function(self.method, cls=objtype)


def update_argspec(spec, args, kwargs):

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
    nargs_remain = nargs_takes - nargs_given
    if no_varargs and nargs_remain < 0:
        raise TypeError(
            "function takes {takes} positional argument but {given} were given"
            .format(
                name=name,
                takes=nargs_takes,
                given=nargs_given,
            )
        )

    new_args = spec.args[nargs_given:]
    new_defaults = spec.defaults[-nargs_remain:] if nargs_remain > 0 else None

    # FIXME:
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


@immutable
class Wrapped():


    """Original function that provides metainformation"""
    __unwrapped = attr.ib()


    """Wrapped function that is actually called"""
    __wrapped = attr.ib()


    def __call__(self, *args, **kwargs):
        return self.__wrapped(*args, **kwargs)


    def __repr__(self):
        return repr(self.__wrapped)


    @property
    def __module__(self):
        return self.__unwrapped.__module__


    @property
    def __signature__(self):
        return inspect.signature(self.__unwrapped)


    @property
    def __doc__(self):
        return self.__unwrapped.__doc__


def wraps(f):
    """Simple wrapping function similar to functools.wraps

    Aims to be a bit simpler and faster, but not sure about it. Experimenting
    at the moment.

    """
    def wrap(g):
        return Wrapped(f, g)
    return wrap


def identity(x):
    """a -> a"""
    return x


class PerformanceWarning(Warning):
    pass


@st.composite
def draw_args(draw, f, *args):
    return f(*(draw(a) for a in args))


@st.composite
def sample_type(draw, types, types1=[], types2=[]):
    if len(types) == 0:
        raise ValueError("Must provide at least one concrete type")
    arg = st.deferred(lambda: sample_type(types, types1, types2))
    return draw(
        st.one_of(
            # Concrete types
            *[st.just(t) for t in types],
            # One-argument type constructors
            *[
                draw_args(t1, arg)
                for t1 in types1
            ],
            # Two-argument type constructors
            *[
                draw_args(t2, arg, arg)
                for t2 in types2
            ],
        )
    )


def sample_sized(e, size=None):
    return (
        e if size is None else
        st.tuples(*(size * [e]))
    )


def eq_test(x, y, data, **kwargs):
    eq = getattr(x, "__eq_test__", lambda v, *_, **__: x == v)
    return eq(y, data, **kwargs)


def assert_output(f):
    """Assert that the output pair elements are equal"""

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        xs = f(*args)
        x0 = xs[0]
        for xi in xs[1:]:
            assert eq_test(x0, xi, **kwargs)
        return

    return wrapped


@singleton
@immutable
class universal_set():
    """Universal set is a set that contains all objects"""

    def __contains__(self, _):
        return True


def make_test_class(C, typeclasses=universal_set):
    """Create a PyTest-compatible test class

    In order to test only some typeclass laws, give the set of typeclasses as
    ``typeclasses`` argument.

    When PyTest runs tests on a class, it creates an instance of the class and
    tests the instance. The class shouldn't have __init__ method. However, we
    want to test class methods, so there's no need to create an instance in the
    first place and it's ok to have any kind of __init__ method. To work around
    this PyTest limitation, we crete a class which doesn't have __init__ and
    when you call it's constructor, you actually don't get an instance of that
    class but instead the class that we wanted to test in the first place.
    PyTest thinks it got an instance of the class but actually we just gave it
    a class.

    So, to run the class method tests for a class SomeClass, add the following
    to some ``test_`` prefixed module:

    .. code-block:: python

        TestSomeClass = make_test_class(SomeClass)

    """

    classes = {cls for cls in C.mro() if cls in typeclasses}

    test_methods = {
        method
        for cls in classes
        for method in cls.__dict__.keys()
        if method.startswith("test_")
    }

    dct = {
        name: getattr(C, name)
        for name in dir(C)
        if name in test_methods
    }

    class MetaTestClass(type):

        __dict__ = dct

    class TestClass(metaclass=MetaTestClass):

        __dict__ = dct

        def __getattr__(self, name):
            return getattr(C, name)

    return TestClass
