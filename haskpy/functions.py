import attr
import functools
import inspect
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid, Cartesian, Cocartesian, Semigroup
from haskpy.types import Nil, Cons
from haskpy.utils import (
    curry,
    identity,
    immutable,
    class_property,
    class_function,
    eq_test,
)
from haskpy import testing


def FunctionMonoid(monoid):
    """Create a function type that has a Monoid instance"""

    @immutable
    class _FunctionMonoid(Monoid, Function):
        """Function type with Monoid instance added"""

        @class_property
        def empty(cls):
            return Function(lambda _: monoid.empty)

        @class_function
        def sample_monoid_type(cls):
            t = monoid.sample_monoid_type()
            return t.map(lambda b: cls.sample_value(None, b))

    return _FunctionMonoid


@immutable
class Function(Monad, Cartesian, Cocartesian, Semigroup):
    """Monad instance for functions

    Use similar wrapping as functools.wraps does for some attributes. See
    CPython: https://github.com/python/cpython/blob/master/Lib/functools.py#L30

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

    # TODO: Add __annotations__

    @class_function
    def pure(cls, x):
        return cls(lambda *args, **kwargs: x)

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
        # TODO: Currying doesn't work nicely here.. Should perhaps compose
        # uncurried functions and then curry the end result?
        return Function(
            lambda *args, **kwargs: g(*args, **kwargs)(
                f(*args, **kwargs)
            )
        )

    def bind(f, g):
        """(a -> b) -> (b -> a -> c) -> a -> c"""
        # TODO: Currying doesn't work nicely here.. Should perhaps compose
        # uncurried functions and then curry the end result?
        return Function(
            lambda *args, **kwargs: g(f(*args, **kwargs))(
                *args,
                **kwargs
            )
        )

    def first(f):
        """(a -> b) -> (a, c) -> (b, c)"""
        return _cross(f, identity)

    def second(f):
        """(a -> b) -> (c, a) -> (c, b)"""
        return _cross(identity, f)

    def left(f):
        """(a -> b) -> Either a c -> Either b c"""
        return _plus(f, identity)

    def right(f):
        """(a -> b) -> Either c a -> Either c b"""
        return _plus(identity, f)

    def append(f, g):
        """(a -> b) -> (a -> b) -> (a -> b)"""
        return f.map(lambda x: lambda y: x.append(y)).apply_to(g)

    def __call__(self, *args, **kwargs):
        # Don't add docstring here because it shows up a bit stupidly in help
        # texts.
        y = self.__f(*args, **kwargs)
        return (
            Function(y)
            if callable(y) and not isinstance(y, Function) else
            y
        )

    def __repr__(self):
        return repr(self.__f)

    @property
    def __module__(self):
        return self.__f.__module__

    # @property
    # def __annotations__(self):
    #     return self.__f.__annotations__

    @property
    def __signature__(self):
        return inspect.signature(self.__f)

    @property
    def __doc__(self):
        return self.__f.__doc__

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
        return testing.sample_function(b).map(Function)

    @class_function
    def sample_semigroup_type(cls):
        t = testing.sample_semigroup_type()
        return t.map(lambda b: cls.sample_value(None, b))


def function(f):
    """Decorator for currying and transforming functions into monads"""
    return Function(curry(f))


@function
def compose(g, f):
    # Problem with composing with *args and **kwargs as:
    #
    #   Function(lambda *args, **kwargs: g(f(*args, **kwargs)))
    #
    # Consider the following:
    #
    #   f = curry(lambda x, y: x + y)
    #
    #   g = lambda z: z * 2
    #
    #   h = compose(g, f)
    #
    # This doesn't work:
    #
    #   h(2)(3)
    #
    # This works:
    #
    #   h(2, 3)
    #
    # Thus, let's use exactly one argument:
    return Function(lambda x: g(f(x)))


@function
def const(x, y):
    """a -> b -> a"""
    return x


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


# NOTE: Functor/Applicative/Monad-related functions couldn't be defined in the
# modules that defined those typeclasses because of circular dependency:
# Function class inherits Monad&Applicative&Functor but the functions in those
# typeclass modules are decorated with Function. Because these dependencies are
# needed already at import-time, there's no way to delay the cross-imports.
# Thus, we now just moved those functions into this module.


#
# Functor-related functions
#

@function
def map(f, x):
    return x.map(f)


@function
def replace(a, x):
    return x.replace(a)


#
# Applicative-related functions
#

@function
def liftA2(f, x, y):
    return x.map(f).apply(y)


@function
def liftA3(f, x, y, z):
    return liftA2(f, x, y).apply(z)


@function
def apply(f, x):
    return x.apply(f)


@function
def sequence(x, y):
    return x.sequence(y)


#
# Monad-related functions
#

@function
def bind(x, f):
    return x.bind(f)


@function
def join(x):
    return x.join()


#
# Contravariant-related functions
#

@function
def contramap(f, x):
    """(a -> b) -> f b -> f a"""
    return x.contramap(f)


@function
def contrareplace(b, x):
    """b -> f b -> f a"""
    return x.contrareplace(b)


#
# Profunctor-related functions
#

@function
def dimap(f, g, x):
    """(a -> b) -> (c -> d) -> p b c -> p a d"""
    return x.dimap(f, g)


#
# Monoid-related functions
#

@function
def append(x, y):
    """m -> m -> m"""
    return x.append(y)


#
# Foldable-related functions
#

@function
def fold_map(monoid, f, xs):
    """(Foldable t, Monoid m) => Monoid -> (a -> m) -> t a -> m

    The first argument is a class of the values inside the foldable structure.
    It must be given explicitly so empty structures can be handled without
    errors.

    """
    return xs.fold_map(monoid, f)


@function
def foldl(combine, initial, xs):
    """Foldable t => (b -> a -> b) -> b -> t a -> b"""
    return xs.foldl(combine, initial)


@function
def foldr(combine, initial, xs):
    """Foldable t => (a -> b -> b) -> b -> t a -> b"""
    return xs.foldr(combine, initial)


@function
def foldr_lazy(combine, initial, xs):
    """Foldable t => (a -> (() -> b) -> (() -> b)) -> b -> t a -> b

    Nonstrict right-associative fold.

    This function is similar to ``foldr`` in Haskell, but note that the combine
    function uses singleton lambda functions to achieve laziness and to enable
    tail-call optimization.

    Let's have a closer look on the signature of ``combine`` to understand the
    possibilities a bit better:

    The signature of ``combine`` is ``a -> (() -> b) -> (() -> b)``. You can
    think of these ``() -> b`` as "lazy" accumulated values. ``() -> b`` is
    just a lambda function that takes no arguments and returns a value of type
    ``b``. Let's name the first argument ``x :: a`` and the second argument
    ``lacc :: () -> b`` (as "lazy accumulator"). Now we can explain how to make
    use of some powerful features:

    - When ``combine`` doesn't use it's second argument ``lacc``, the recursion
      stops (i.e., short-circuits). Therefore, infinite lists might be
      processed in finite time.

    - When ``combine`` returns ``lacc`` as such without modifying it, tail-call
      optimization triggers. Therefore, very long lists might be processed
      efficiently without exceeding maximum recursion depth or overflowing the
      stack.

    - When ``combine`` uses ``lacc`` but the evaluation ``lacc()`` is
      "post-poned" (e.g., it happens inside yet another lambda function), the
      recursion becomes "lazy" as it will continue only when ``lacc()``
      actually gets evaluated. Therefore, infinite lists can be processed
      lazily.

    Note that Python's built-in ``reduce`` function doesn't support these
    features.

    Examples
    --------

    Short-circuiting and tail-call optimization for an infinite list:

    >>> xs = iterate(lambda x: x + 1, 1)
    >>> my_any = foldr_lazy(lambda x, lacc: (lambda: True) if x else lacc, False)
    >>> my_any(xs.map(lambda x: x > 100000))
    True

    Looking at ``(lambda: True) if x else lacc``, we can see that when the left
    side of the if-expression is evaluated, the fold short-circuits because
    ``True`` makes no use of ``lacc``. When the right side of the if-expression
    is evaluated, the fold uses efficient tail-call optimization because
    ``lacc`` is returned unmodified.

    Lazy evaluation makes it possible to transform infinite structures:

    >>> from haskpy import Cons, Nil
    >>> my_map = lambda f: foldr_lazy(lambda x, lacc: lambda: Cons(f(x), lacc), Nil)
    >>> my_map(lambda x: x ** 2)(xs)
    Cons(1, Cons(4, Cons(9, Cons(16, Cons(25, Cons(36, ...))))))

    The infinite list gets mapped lazily because ``lacc`` isn't called at this
    time, it is delayed as the linked list will call it only when the next
    element is requested.

    Note that sometimes you shouldn't use ``foldr_lazy`` because it can cause
    stack overflow (or rather hit Python's recursion limit) because of too deep
    recursion. This can happen with a long list when the recursion doesn't
    short-circuit (early enough), tail-call optimization cannot be used and the
    recursion doesn't pause for laziness. A simple such example is a summation:

    >>> my_sum = foldr_lazy(lambda x, lacc: lambda: x + lacc(), 0)
    >>> my_sum(xs.take(100))
    5050
    >>> my_sum(xs.take(1000000))
    Error

    For this kind of folds, you should use ``foldl``.

    As already shown, ``foldr_lazy`` generalizes ``map`` and ``any``. It can
    also be used to implement many other functions in a may that may seem a bit
    surprising at first, for instance:

    >>> from haskpy import Just, Nothing
    >>> my_head = foldr_lazy(lambda x, lacc: lambda: Just(x), Nothing)
    >>> my_head(xs)
    Just(1)
    >>> my_head(Nil)
    Nothing

    """
    return xs.foldr_lazy(combine, initial)


@function
def fold(monoid, xs):
    """(Foldable t, Monoid m) => Monoid -> t a -> m

    The first argument is a class of the values inside the foldable structure.
    It must be given explicitly so empty structures can be handled without
    errors.

    """
    return xs.fold(monoid)


@function
def length(xs):
    """Foldable t => t a -> int"""
    return xs.length()


@function
def sum(xs):
    """(Foldable t, Num a) => t a -> a"""
    return xs.sum()


@function
def null(xs):
    """Foldable t => t a -> Bool"""
    return xs.null()


@function
def elem(e, xs):
    """(Foldable t, Eq a) => a -> t a -> Bool"""
    return xs.elem(e)


#
# Eq-specific functions
#

@function
def eq(x, y):
    """Equality: ``Eq a => a -> a -> Bool``"""
    return x == y


@function
def ne(x, y):
    """Inequality: ``Eq a => a -> a -> Bool``"""
    return x != y


#
# Either-specific functions
#

@function
def either(f, g, e):
    """(a -> c) -> (b -> c) -> Either a b -> c"""
    return e.match(Left=f, Right=g)


#
# Linked list specific functions
#

@function
def iterate(f, x):
    return Cons(x, lambda: iterate(f, f(x)))


@function
def repeat(x):
    xs = Cons(x, lambda: xs)
    return xs


@function
def replicate(n, x):
    return (
        Nil if n <= 0 else
        Cons(x, lambda: replicate(n - 1, x))
    )

#
# Pattern matching related functions
#
# NOTE: Currying doesn't work as expected for this function, because this is a
# generic function and we don't know how many arguments are required. We would
# first like to get all the required arguments and only after that the actual
# object on which to pattern match. One solution would be take the patterns as
# a dictionary. Then this function would always take two arguments and it would
# be explicit that all the patterns would be given at the same time. Something
# like:
#
@function
# def match(patterns, x):
#     return x.match(**patterns)
#
# Is it better than:
@function
def match(**kwargs):
    return lambda x: x.match(**kwargs)
