import attr
import functools
import inspect
from hypothesis import given
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid
from haskpy.utils import curry, identity, sample_sized
from haskpy import conftest, testing


class _FunctionMeta(type(Monad), type(Monoid)):


    @property
    def empty(cls):
        return cls(identity)


    def pure(cls, x):
        return cls(lambda *args, **kwargs: x)


    def sample_value(cls, a):
        return testing.sample_function(a).map(Function)


@attr.s(frozen=True, repr=False, cmp=False)
class Function(Monad, Monoid, metaclass=_FunctionMeta):
    """Monad instance for functions

    Use similar wrapping as functools.wraps does for some attributes. See
    CPython: https://github.com/python/cpython/blob/master/Lib/functools.py#L30

    """


    # NOTE: Currying functions is a bit slow (mainly because of
    # functools.wraps). So don't use converter=curry here. Instead provide a
    # decorator ``function`` which combines Function and curry.
    __f = attr.ib()


    # TODO: Add __annotations__


    def __Function(self, f):
        # Instead of using self.__Function(f) to create a new Function
        # instance, we could just use Function(f). But that doesn't work in
        # tests, where we are using a subclass _TestClass. We need to create
        # instances of that test class in tests, so this makes it work in both
        # cases.
        return attr.evolve(self, Function__f=f)


    def map(f, g):
        """(a -> b) -> (b -> c) -> (a -> c)"""
        return f.__Function(lambda x: g(f(x)))


    def apply(f, g):
        """(a -> b) -> (a -> b -> c) -> a -> c"""
        # TODO: Currying doesn't work nicely here.. Should perhaps compose
        # uncurried functions and then curry the end result?
        return f.__Function(
            lambda *args, **kwargs: g(*args, **kwargs)(
                f(*args, **kwargs)
            )
        )


    def bind(f, g):
        """(a -> b) -> (b -> a -> c) -> a -> c"""
        # TODO: Currying doesn't work nicely here.. Should perhaps compose
        # uncurried functions and then curry the end result?
        return f.__Function(
            lambda *args, **kwargs: g(f(*args, **kwargs))(
                *args,
                **kwargs
            )
        )


    def append(f, g):
        """(a -> a) -> (a -> a) -> (a -> a)"""
        # FIXME: compose(f, g) or compose(g, f) ????
        #
        # FIXME: This is wrong for functions in general. It's some endofunction
        # stuff.
        return compose(f, g)


    def __call__(self, *args, **kwargs):
        # Don't add docstring here because it shows up a bit stupidly in help
        # texts.
        y = self.__f(*args, **kwargs)
        return (
            self.__Function(y)
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
            return self.__Function(fp)
        else:
            # Class method
            return self


    def __test_eq__(self, g, data):
        # NOTE: This is used only in tests when the function input doesn't
        # really matter so any hashable type here is ok. The type doesn't
        # matter because the functions are either _TestFunction or created with
        # pure.
        x = data.draw(st.integers())
        return self(x) == g(x)


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
# PatternMatchable-related functions
#
# NOTE: Currying doesn't work as expected for this function, because this is a
# generic function and we don't know how many arguments are required. We would
# first like to get all the required arguments and only after that the actual
# object on which to pattern match. One solution would be take the patterns as
# a dictionary. Then this function would always take two arguments and it would
# be explicit that all the patterns would be given at the same time. Something
# like:
#
# @function
# def match(patterns, x):
#     return x.match(**patterns)
#
# Is it better than:
@function
def match(**kwargs):
    return lambda x: x.match(**kwargs)
