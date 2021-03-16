"""Uncurried functions that are similar to normal Python functions

.. autosummary::
   :toctree:

   UncurriedFunction
   UncurriedFunctionMonoid

.. autosummary::
   :toctree:

   uncurried

"""
import attr
import functools
import inspect
from hypothesis import strategies as st

from haskpy.typeclasses._monad import Monad
from haskpy.typeclasses._monoid import Monoid
from haskpy.typeclasses._semigroup import Semigroup

from haskpy.internal import (
    immutable,
    class_property,
    class_function,
)
from haskpy.testing import eq_test
from haskpy import testing


def UncurriedFunctionMonoid(monoid):
    """Create a function type that has a Monoid instance"""

    @immutable
    class _UncurriedFunctionMonoid(Monoid, UncurriedFunction):
        """Function type with Monoid instance added"""

        @class_property
        def empty(cls):
            return _UncurriedFunctionMonoid(lambda *args, **kwargs: monoid.empty)

        @class_function
        def sample_monoid_type(cls):
            t = monoid.sample_monoid_type()
            return t.map(lambda b: cls.sample_value(None, b))

    return _UncurriedFunctionMonoid


@immutable
class UncurriedFunction(Monad, Semigroup):
    """Monad instance for normal Python functions

    The functions can take any number of positional and keyword arguments, so
    the signature can be anything supported by Python. The function must be
    called by passing all arguments at the same time, so it doesn't support
    automatic partial evaluation like :py:class:`.Function`. One way to think
    of this in type level is that the collection of all positional and keyword
    arguments are represented by type ``Args``. So, the type of
    ``UncurriedFunction`` is ``Args -> a``. This is a bit notational abuse as
    ``Args`` cannot be an output of a function, only an input. So, type ``a ->
    Args`` makes no sense. This means that one cannot compose these functions
    in a way that would pass ``Args`` to the next function because a function
    can only output a single value, not many values.

    .. note::

        Monoid instance of UncurriedFunction requires the knowledge of the
        contained monoid type in order to be able to create ``empty``. The
        contained type is not known because Function class can be used to
        create functions of any type. This is just convenience and simpler user
        interface. If you need Monoid instance of UncurriedFunction, use
        UncurriedFunctionMonoid function to create such a class. Note though
        that the Semigroup instance is available in this Function without
        needing to use UncurriedFunctionMonoid.

    """

    __f = attr.ib(validator=lambda _, __, f: callable(f))

    def __attrs_post_init__(self):
        object.__setattr__(self, "__qualname__", self.__f.__qualname__)
        object.__setattr__(self, "__module__", self.__f.__module__)
        object.__setattr__(self, "__doc__", self.__f.__doc__)
        object.__setattr__(self, "__name__", self.__f.__name__)
        #object.__setattr__(self, "__annotations__", self.__f.__annotations__)
        object.__setattr__(self, "__defaults__", None)
        object.__setattr__(self, "__kwdefaults__", None)
        return

    @property
    def __code__(self):
        return self.__f.__code__

    @property
    def __signature__(self):
        return inspect.signature(self.__f)

    @class_function
    def pure(cls, x):
        return cls(lambda *_, **__: x)

    def map(f, g):
        """(Args -> b) -> (b -> c) -> (Args -> c)"""
        return UncurriedFunction(lambda *args, **kwargs: g(f(*args, **kwargs)))

    def apply(f, g):
        """(Args -> b) -> (Args -> b -> c) -> Args -> c"""
        return UncurriedFunction(
            lambda *args, **kwargs: g(*args, **kwargs)(f(*args, **kwargs))
        )

    def bind(f, g):
        """(Args -> b) -> (b -> Args -> c) -> Args -> c"""
        return UncurriedFunction(
            lambda *args, **kwargs: g(f(*args, **kwargs))(*args, **kwargs)
        )

    def append(f, g):
        """Semigroup b => (Args -> b) -> (Args -> b) -> (Args -> b)"""
        return f.map(lambda x: lambda y: x.append(y)).apply_to(g)

    def __call__(self, *args, **kwargs):
        return self.__f(*args, **kwargs)

    def __repr__(self):
        return repr(self.__f)

    def __pow__(self, x):
        # We need to implement __pow__ for UncurriedFunction objects because
        # otherwise composing UncurriedFunction objects wouldn't be possible:
        # If f and g are UncurriedFunction objects in f ** g, Python will try
        # f.__pow__(g) and if it fails, it won't try g.__rpow__(f) because it
        # already concluded that UncurriedFunction object doesn't support pow
        # operation with a UncurriedFunction object.
        return x.__rpow__(self)

    def __get__(self, obj, objtype):
        """Support instance methods.

        See: https://stackoverflow.com/a/3296318

        """
        if obj is not None:
            # Instance method, bind the first argument
            fp = functools.partial(self, obj)
            # Keep the docstring untouched
            fp.__doc__ = self.__doc__
            return UncurriedFunction(fp)
        else:
            # Class method
            return self

    def __eq_test__(self, g, data, input_strategy=st.integers()):
        # NOTE: This is used only in tests when the function input doesn't
        # really matter so any hashable type here is ok. The type doesn't
        # matter because the functions are either _TestFunction or created with
        # pure.
        x = data.draw(input_strategy)
        return eq_test(self(x), g(x), data)

    @class_function
    def sample_value(cls, _, b):
        return testing.sample_function(b).map(cls)

    sample_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_type(),
    )

    sample_semigroup_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_semigroup_type(),
    )

    sample_monoid_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_monoid_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler(
        testing.sample_hashable_type(),
    )
    sample_apply_type_constructor = sample_functor_type_constructor
    sample_applicative_type_constructor = sample_functor_type_constructor
    sample_monad_type_constructor = sample_functor_type_constructor


def uncurried(f):
    """Decorator for transforming functions into monads

    This can be useful for converting value constructors into function monads,
    so that one can use ``map`` and other methods of a function monad. For
    instance, ``List`` is a value constructor but doesn't have monadic methods.
    By wrapping it with ``uncurried``, you can treat it like a normal uncurried
    function:

    .. code-block:: python

        >>> from haskpy import List, Maybe, Just
        >>> MaybeList = uncurried(List).map(lambda xs: xs.sequence(Maybe))
        >>> MaybeList(Just(10), Just(20), Just(30))
        Just(List(10, 20, 30))

    The above example converted ``List`` constructor into a special constructor
    that converts ``List (Maybe a)`` into ``Maybe (List a)`` automatically.
    This can be useful so that you can easily create lists inside your own
    custom monads.

    """
    # Don't wrap twice
    return f if isinstance(f, UncurriedFunction) else UncurriedFunction(f)
