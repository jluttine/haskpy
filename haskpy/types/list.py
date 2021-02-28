import attr
import functools
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid, Foldable, Eq
from haskpy import testing
from haskpy.utils import (
    immutable,
    class_property,
    class_function,
    eq_test,
)
from haskpy.functions import function


@immutable(init=False)
class List(Monad, Monoid, Foldable, Eq):

    __xs = attr.ib(converter=tuple)

    def __init__(self, *xs):
        object.__setattr__(self, "_List__xs", tuple(xs))
        return

    def map(self, f):
        """List a -> (a -> b) -> List b"""
        return List(*(f(x) for x in self.__xs))

    @class_function
    def pure(cls, x):
        """a -> List a"""
        return cls(x)

    def apply(self, fs):
        """List a -> List (a -> b) -> List b"""
        return List(*(y for f in fs.__xs for y in self.map(f).__xs))

    def bind(self, f):
        """List a -> (a -> List b) -> List b"""
        return List(*(y for ys in self.map(f).__xs for y in ys.__xs))

    def __eq__(self, other):
        """List a -> List a -> bool"""
        return self.__xs == other.__xs

    @class_property
    def empty(cls):
        """Empty list, type ``List a``"""
        return cls()

    def append(self, xs):
        """List a -> List a -> List a"""
        return List(*self.__xs, *xs.__xs)

    def to_iter(self):
        yield from self.__xs

    @class_function
    def from_iter(cls, xs):
        """Iterable f => f a -> List a"""
        return cls(*xs)

    def length(self):
        return len(self.__xs)

    def elem(self, e):
        return e in self.__xs

    def foldl(self, combine, initial):
        """List a -> (b -> a -> b) -> b -> b

        ``combine`` function is assumed to be curried

        """
        # TODO: We could implement also fold_map to make fold_map and fold to
        # use parallelized implementation because they use monoids. Now, the
        # default implementations use foldl/foldr which both are sequential.
        return functools.reduce(
            lambda a, b: combine(a)(b),
            self.__xs,
            initial,
        )

    def foldr(self, combine, initial):
        """List a -> (a -> b -> b) -> b -> b

        ``combine`` function is assumed to be curried

        """
        # TODO: We could implement also fold_map to make fold_map and fold to
        # use parallelized implementation because they use monoids. Now, the
        # default implementations use foldl/foldr which both are sequential.
        return functools.reduce(
            lambda b, a: combine(a)(b),
            self.__xs[::-1],
            initial,
        )

    def __repr__(self):
        return "List{}".format(repr(self.__xs))

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_value(cls, a):
        return st.lists(a, max_size=10).map(lambda xs: cls(*xs))

    sample_type = testing.sample_type_from_value(
        testing.sample_type(),
    )

    sample_functor_type = testing.sample_type_from_value()
    sample_applicative_type = sample_functor_type
    sample_monad_type = sample_functor_type

    sample_semigroup_type = testing.sample_type_from_value(
        testing.sample_type(),
    )
    sample_monoid_type = sample_semigroup_type

    sample_eq_type = testing.sample_type_from_value(
        testing.sample_eq_type(),
    )

    sample_foldable_type = testing.sample_type_from_value()
    sample_foldable_functor_type = sample_foldable_type

    def __eq_test__(self, other, data=None):
        return (
            False if len(self.__xs) != len(other.__xs) else
            all(
                eq_test(x, y, data)
                for (x, y) in zip(self.__xs, other.__xs)
            )
        )
