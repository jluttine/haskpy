"""Functions

.. autosummary::
   :toctree:

   Function
   FunctionMonoid

.. autosummary::
   :toctree:

   function
   compose

"""
import attr
import functools
import inspect
from hypothesis import strategies as st

from haskpy.typeclasses._monad import Monad
from haskpy.typeclasses._monoid import Monoid
from haskpy.typeclasses._cartesian import Cartesian
from haskpy.typeclasses._cocartesian import Cocartesian
from haskpy.typeclasses._semigroup import Semigroup

from haskpy.internal import (
    immutable,
    class_property,
    class_function,
)
from haskpy.testing import eq_test
from haskpy import testing


@immutable
class _Code():

    co_argcount = attr.ib()
    co_flags = attr.ib()


def FunctionMonoid(monoid):
    """Create a function type that has a Monoid instance"""

    @immutable
    class _FunctionMonoid(Monoid, Function):
        """Function type with Monoid instance added"""

        @class_property
        def empty(cls):
            return _FunctionMonoid(lambda _: monoid.empty)

        @class_function
        def sample_monoid_type(cls):
            t = monoid.sample_monoid_type()
            return t.map(lambda b: cls.sample_value(None, b))

    return _FunctionMonoid


@immutable
class Function(Monad, Cartesian, Cocartesian, Semigroup):
    """Monad instance for curried functions ``:: a -> b``

    The function is curried in such a way that the function can be applied one
    argument at a time, all arguments at the same time or the arguments divided
    arbitrarily among multiple calls. To illustrate this, consider the
    following two-argument function that returns another two-argument function:

    .. code-block:: python

        @function
        def foo(a, b):

            @function
            def bar(c, d):
                return a + b + c + d

            return bar

    This is effectively a four-argument function for which any of the following
    examples is a valid way of calling it:

    .. code-block:: python

        >>> foo("a")("b")("c")("d")
        'abcd'
        >>> foo("a", "b", "c", "d")
        'abcd'
        >>> foo("a")("b", "c")("d")
        'abcd'

    Function composition is equivalent to functorial mapping over a function.
    Therefore, functions can be composed at least in any of the following three
    ways:

    .. code-block:: python

        >>> import haskpy as hp
        >>> f = hp.function(lambda x: x + 3)
        >>> g = lambda x: 2 * x
        >>> h = lambda x: x ** 2
        >>> (h ** g ** f)(2)
        100
        >>> hp.map(h, hp.map(g, f))(2)
        100
        >>> f.map(g).map(h)(2)
        100

    Here, ``**`` for functions (or functors) means composing (or functorial
    mapping).

    Note that ``Function`` objects accept only positional arguments. The number
    of those positional arguments is exactly the same as the number of required
    positional arguments in the underlying function. Any optional positional or
    keyword arguments become unusable. The reason for this is that it must be
    unambiguous at which point, for instance, ``map`` is applied. Also,
    ``f(a)(b)`` should always be equal to ``f(a, b)`` with curried functions.
    This might not be the case if there are optional arguments.

    .. note::

        Monoid instance of Function requires the knowledge of the contained
        monoid type in order to be able to create ``empty``. The contained type
        is not known because Function class can be used to create functions of
        any type. This is just convenience and simpler user interface. If you
        need Monoid instance of Function, use FunctionMonoid function to create
        such a class. Note though that the Semigroup instance is available in
        this Function without needing to use FunctionMonoid.

    """

    # NOTE: Currying functions is a bit slow (mainly because of
    # functools.wraps). So don't use converter=curry here. Instead provide a
    # decorator ``function`` which combines Function and curry.
    __f = attr.ib()

    __args = attr.ib(default=(), converter=tuple)

    def __attrs_post_init__(self):
        object.__setattr__(self, "__qualname__", self.__f.__qualname__)
        object.__setattr__(self, "__module__", self.__f.__module__)
        object.__setattr__(self, "__doc__", self.__f.__doc__)
        object.__setattr__(self, "__name__", self.__f.__name__)
        object.__setattr__(self, "__annotations__", self.__f.__annotations__)
        object.__setattr__(self, "__defaults__", None)
        object.__setattr__(self, "__kwdefaults__", None)
        return

    @property
    def __code__(self):
        # We use __code__.co_argcount attribute in this Function class, so
        # let's add this attribute to Function objects too so that we can wrap
        # Function objects with Function class.
        return _Code(
            co_argcount=self.__f.__code__.co_argcount - len(self.__args),
            # co_flags is needed by Sphinx for some reason..
            co_flags=self.__f.__code__.co_flags,
        )

    @property
    def __signature__(self):
        return inspect.signature(self.__f)

    @__f.validator
    def check_f(self, attribute, value):
        if not callable(value):
            raise ValueError("The function must a callable")
        nargs = value.__code__.co_argcount
        if nargs == 0:
            raise ValueError(
                "The function must have at least one required positional "
                "argument"
            )
        return

    @__args.validator
    def check_args(self, attribute, value):
        if len(value) >= self.__f.__code__.co_argcount:
            raise ValueError()
        return

    # TODO: Add __annotations__

    @class_function
    def pure(cls, x):
        return cls(lambda _: x)

    def dimap(f, g, h):
        """(b -> c) -> (a -> b) -> (c -> d) -> (a -> d)"""
        return Function(lambda x: h(f(g(x))))

    def map(f, g):
        """(a -> b) -> (b -> c) -> (a -> c)"""
        return Function(lambda x: g(f(x)))

    def contramap(f, g):
        """(b -> c) -> (a -> b) -> (a -> c)"""
        return Function(lambda a: f(g(a)))

    def apply(f, g):
        """(a -> b) -> (a -> b -> c) -> a -> c"""
        return Function(lambda x: g(x)(f(x)))

    def bind(f, g):
        """(a -> b) -> (b -> a -> c) -> a -> c"""
        return Function(lambda x: g(f(x))(x))

    def first(f):
        """(a -> b) -> (a, c) -> (b, c)"""
        from haskpy.utils import identity
        return _cross(f, identity)

    def second(f):
        """(a -> b) -> (c, a) -> (c, b)"""
        from haskpy.utils import identity
        return _cross(identity, f)

    def left(f):
        """(a -> b) -> Either a c -> Either b c"""
        from haskpy.utils import identity
        return _plus(f, identity)

    def right(f):
        """(a -> b) -> Either c a -> Either c b"""
        from haskpy.utils import identity
        return _plus(identity, f)

    def append(f, g):
        """(a -> b) -> (a -> b) -> (a -> b)"""
        return f.map(lambda x: lambda y: x.append(y)).apply_to(g)

    def __call__(self, *args):
        # Don't add docstring here because it shows up a bit stupidly in help
        # texts.

        args = self.__args + args

        n = self.__f.__code__.co_argcount
        m = len(args)

        if m < n:
            # Function partially applied.
            return attr.evolve(self, Function__args=args)
        elif m == n:
            # Function fully applied
            return self.__f(*args)
        else:
            # Function fully applied and some arguments left over
            return self.__f(*args[:n])(*args[n:])

    def __repr__(self):
        return repr(self.__f)

    def __pow__(self, x):
        # We need to implement __pow__ for Function objects because otherwise
        # composing Function objects wouldn't be possible: If f and g are
        # Function objects in f ** g, Python will try f.__pow__(g) and if it
        # fails, it won't try g.__rpow__(f) because it already concluded that
        # Function object doesn't support pow operation with a Function object.
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
            return Function(fp)
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

    @class_function
    def sample_contravariant_type_constructor(cls):
        return testing.sample_type().map(
            lambda b: lambda a: cls.sample_value(a, b)
        )
        # return st.tuples(a, testing.sample_type()).map(
        #     lambda args: cls.sample_value(*args)
        # )

    sample_profunctor_type_constructor = testing.create_type_constructor_sampler()
    sample_cartesian_type_constructor = sample_profunctor_type_constructor
    sample_cocartesian_type_constructor = sample_profunctor_type_constructor


def function(f):
    """Decorator for currying and transforming functions into monads"""
    # Don't wrap twice
    return f if isinstance(f, Function) else Function(f)


@function
def compose(f, g):
    return function(g).map(f)


@function
def _cross(f, g, ab):
    """(a -> c) -> (b -> d) -> (a, b) -> (c, d)"""
    return (f(ab[0]), g(ab[1]))


@function
def _plus(f, g, eab):
    """(a -> c) -> (b -> d) -> Either a b -> Either c d"""
    # FIXME: Once Bifunctor has been implemented, just use:
    # eab.bimap(f, g)
    from haskpy.types.either import Left, Right
    return eab.match(Left=lambda a: Left(f(a)), Right=lambda b: Right(g(b)))
