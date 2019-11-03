import attr
import functools
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid, Foldable
from haskpy.utils import sample_type, sample_sized


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


    def sample(cls, a=None, **kwargs):
        elements = (
            st.just(a) if a is not None else
            sample_type(
                types=[
                    st.integers(),
                    st.lists(st.integers()),
                ],
                types1=[
                    List.sample,
                    cls.sample,
                ]
            )
        )
        return elements.flatmap(
            lambda e: sample_sized(
                st.lists(e, max_size=10).map(lambda xs: cls(*xs)),
                **kwargs
            )
        )


    def sample_functor(cls, elements):
        return st.lists(elements, max_size=10).map(lambda xs: cls(*xs))


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
