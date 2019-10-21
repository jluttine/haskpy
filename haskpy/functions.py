import attr
import functools
import inspect

from haskpy.typeclasses import Monad, Monoid
from haskpy.utils import curry, identity


class _FunctionMeta(type(Monad), type(Monoid)):


    @property
    def empty(cls):
        return Function(identity)


    def pure(cls, x):
        return Function(lambda *args, **kwargs: x)


@attr.s(frozen=True, repr=False)
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


    def map(f, g):
        """(a -> b) -> (b -> c) -> (a -> c)"""
        return compose(g, f)


    def append(f, g):
        """(a -> a) -> (a -> a) -> (a -> a)"""
        # FIXME: compose(f, g) or compose(g, f) ????
        return compose(f, g)


    def __call__(self, *args, **kwargs):
        # Don't add docstring here because it shows up a bit stupidly in help
        # texts.
        y = self.__f(*args, **kwargs)
        return Function(y) if callable(y) else y


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


def function(f):
    """Decorator for currying and transforming functions into monads"""
    return Function(curry(f))


@function
def compose(g, f):
    return Function(lambda *args, **kwargs: g(f(*args, **kwargs)))


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
def apply(f, x):
    return x.apply(f)


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
