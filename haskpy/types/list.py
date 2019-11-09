import attr
import functools
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid, Foldable
from haskpy.utils import sample_type, sample_sized
from haskpy import testing
from haskpy.functions import curry


class _ListMeta(type(Monad), type(Monoid), type(Foldable)):


    @property
    def empty(cls):
        return cls()


    def pure(cls, x):
        """a -> List a"""
        return cls(x)


    def from_iter(cls, xs):
        """Iterable f => f a -> List a"""
        return cls(*xs)


    def sample_value(cls, a):
        return st.lists(a, max_size=10).map(lambda xs: cls(*xs))


    def sample_monoid_type(cls):
        t = testing.sample_type()
        return t.map(cls.sample_value)


@attr.s(frozen=True, repr=False, init=False)
class List(Monad, Monoid, Foldable, metaclass=_ListMeta):


    __xs = attr.ib(converter=tuple)


    def __init__(self, *xs):
        object.__setattr__(self, "_List__xs", tuple(xs))
        return


    def map(self, f):
        """List a -> (a -> b) -> List b"""
        return List(*(f(x) for x in self.__xs))


    def apply(self, fs):
        """List a -> List (a -> b) -> List b"""
        return List(*(y for f in fs.__xs for y in self.map(f).__xs))


    def bind(self, f):
        """List a -> (a -> List b) -> List b"""
        return List(*(y for ys in self.map(f).__xs for y in ys.__xs))


    def append(self, xs):
        """List a -> List a -> List a"""
        return List(*self.__xs, *xs.__xs)


    def to_iter(self):
        yield from self.__xs


    def length(self):
        return len(self.__xs)


    def elem(self, e):
        return e in self.__xs


    def foldl(self, combine, initial):
        """List a -> (b -> a -> b) -> b -> b"""
        # TODO: We could implement also fold_map to make fold_map and fold to
        # use parallelized implementation because they use monoids. Now, the
        # default implementations use foldl/foldr which both are sequential.
        return functools.reduce(
            lambda a, b: curry(combine)(a)(b),
            self.__xs,
            initial,
        )


    def foldr(self, combine, initial):
        """List a -> (a -> b -> b) -> b -> b"""
        # TODO: We could implement also fold_map to make fold_map and fold to
        # use parallelized implementation because they use monoids. Now, the
        # default implementations use foldl/foldr which both are sequential.
        return functools.reduce(
            lambda b, a: curry(combine)(a)(b),
            self.__xs[::-1],
            initial,
        )


    def __repr__(self):
        return "List{}".format(repr(self.__xs))
