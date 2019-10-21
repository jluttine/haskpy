import attr
import functools

from haskpy.typeclasses import Monad, Monoid, Foldable


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


    def foldl(self, combine, initial):
        """List a -> (b -> a -> b) -> b -> b"""
        # TODO: We could implement also fold_map to make fold_map and fold to
        # use parallelized implementation because they use monoids. Now, the
        # default implementations use foldl/foldr which both are sequential.
        return functools.reduce(
            combine,
            self.__xs,
            initial,
        )


    def foldr(self, combine, initial):
        """List a -> (a -> b -> b) -> b -> b"""
        # TODO: We could implement also fold_map to make fold_map and fold to
        # use parallelized implementation because they use monoids. Now, the
        # default implementations use foldl/foldr which both are sequential.
        return functools.reduce(
            lambda b, a: combine(a, b),
            self.__xs[::-1],
            initial,
        )


    def __repr__(self):
        return "List{}".format(repr(self.__xs))
