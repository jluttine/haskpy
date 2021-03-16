import hypothesis.strategies as st
import attr
import functools

from haskpy.internal import immutable, class_function, universal_set


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


def types():
    from haskpy import All, String, Maybe
    from haskpy.types import hypothesis
    # Some example types. The more types you add here, the longer it takes to
    # run the tests. Also, put simpler non-recursive strategies first:
    # https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.one_of
    return (
        All,
        hypothesis.HypothesisInteger,
        String,
        Maybe,
    )


def sample_type_of(f, depth=0):

    def try_sample(cls):
        try:
            return f(cls)
        except AttributeError:
            return st.nothing()

    # NOTE: 1) Use deferring to work with the circular dependency in the type
    # modules: they import this module and types() function imports them. 2)
    # First select the type, then apply try_sample to it. If one would apply
    # try_sample to all types and then select one of the results, it would lead
    # to infinite recursion as all possible paths are traversed. 3) Use flatmap
    # instead of map!
    return st.deferred(
        lambda: st.sampled_from(types())
    ).flatmap(try_sample)


def sample_type():
    return sample_type_of(lambda cls: cls.sample_type())


def sample_hashable_type():
    return sample_type_of(lambda cls: cls.sample_hashable_type())


def sample_semigroup_type():
    return sample_type_of(lambda cls: cls.sample_semigroup_type())


def sample_monoid_type():
    return sample_type_of(lambda cls: cls.sample_monoid_type())


def sample_commutative_type():
    return sample_type_of(lambda cls: cls.sample_commutative_type())


def sample_eq_type():
    return sample_type_of(lambda cls: cls.sample_eq_type())


@st.composite
def sample_function(draw, b):
    return memoize(lambda _: draw(b))


@st.composite
def sample_uncurried_function(draw, b):
    return memoize_uncurried(lambda *_, **__: draw(b))


def sample_class(typeclass):
    return st.sampled_from(
        tuple(filter(lambda cls: issubclass(cls, typeclass), types()))
    )


def create_type_constructor_sampler(*arg_type_strategies):

    @class_function
    def sample_type_constructor(cls):

        def sample_concrete_type(arg_value_strategies):
            def sample_value(*other_arg_value_strategies):
                return cls.sample_value(
                    *arg_value_strategies,
                    *other_arg_value_strategies,
                )
            return sample_value

        return st.tuples(*arg_type_strategies).map(sample_concrete_type)

    return sample_type_constructor


def create_type_sampler(*arg_type_strategies):

    @class_function
    def sample(cls, *other_arg_value_strategies):
        y = st.tuples(*arg_type_strategies).map(
            lambda arg_value_strategies: cls.sample_value(
                *arg_value_strategies,
                *other_arg_value_strategies,
            )
        )
        return y
    return sample


@immutable
class memoize():

    __f = attr.ib()
    __memory = attr.ib(factory=list, init=False)

    def __attrs_post_init__(self):
        object.__setattr__(self, "__qualname__", self.__f.__qualname__)
        object.__setattr__(self, "__name__", self.__f.__name__)
        object.__setattr__(self, "__annotations__", self.__f.__annotations__)
        object.__setattr__(self, "__defaults__", None)
        object.__setattr__(self, "__kwdefaults__", None)
        return

    def __call__(self, x):
        for (key, value) in self.__memory:
            if key == x:
                return value
        y = self.__f(x)
        self.__memory.append((x, y))
        return y

    @property
    def __code__(self):
        return self.__f.__code__


def memoize_uncurried(f):

    @memoize
    def packed(args_kwargs):
        return f(*args_kwargs[0], **args_kwargs[1])

    return lambda *args, **kwargs: packed((args, kwargs))
