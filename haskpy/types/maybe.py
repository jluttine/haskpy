import attr
import hypothesis.strategies as st
from hypothesis import given

from haskpy.typeclasses import (
    Monad,
    CommutativeMonoid,
    PatternMatchable,
    Hashable,
    Foldable,
)
from .monadtransformer import MonadTransformer
from haskpy.utils import singleton, sample_type, sample_sized

from haskpy import testing


class _MaybeMeta(type(Monad), type(CommutativeMonoid), type(Hashable), type(Foldable)):


    @property
    def empty(cls):
        return Nothing


    def pure(cls, x):
        return Just(x)


    def sample_value(cls, a):
        return st.one_of(a.map(Just), st.just(Nothing))


    def sample_hashable_type(cls):
        t = testing.sample_hashable_type()
        return t.map(cls.sample_value)


    def sample_monoid_type(cls):
        t = testing.sample_monoid_type()
        return t.map(cls.sample_value)


    def sample_commutative_type(cls):
        t = testing.sample_commutative_type()
        return t.map(cls.sample_value)


# Some thoughts on design: One could implement all the methods (except match)
# in Maybe class by using the match method to choose the implementation. But
# this would be just clumsy and add overhead. Class inheritance is a Pythonic
# way of choosing the correct method implementation. Also, Just needs to
# support equality testing, so that's also easy to achieve by making it a
# class.


@attr.s(frozen=True, repr=False)
class Maybe(Monad, CommutativeMonoid, PatternMatchable, Hashable, Foldable,
            metaclass=_MaybeMeta):
    """Maybe type for optional values"""


    def match(self, *, Just, Nothing):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Just(Maybe):


    __x = attr.ib()


    def match(self, *, Just, Nothing):
        return Just(self.__x)


    def map(self, f):
        return Just(f(self.__x))


    def apply_to(self, x):
        return x.map(self.__x)


    def bind(self, f):
        return f(self.__x)


    def append(self, m):
        return m.match(
            Nothing=lambda: self,
            Just=lambda x: Just(self.__x.append(x))
        )


    def fold_map(self, monoid, f):
        return f(self.__x)


    def foldl(self, combine, initial):
        return combine(initial, self.__x)


    def foldr(self, combine, initial):
        return combine(self.__x, initial)


    def __repr__(self):
        return "Just({0})".format(repr(self.__x))


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Maybe):


    def match(self, *, Just, Nothing):
        return Nothing()


    def map(self, f):
        return Nothing


    def apply_to(self, x):
        return Nothing


    def bind(self, f):
        return Nothing


    def append(self, m):
        return m


    def fold_map(self, monoid, f):
        return monoid.empty


    def foldl(self, combine, initial):
        return initial


    def foldr(self, combine, initial):
        return initial


    def __repr__(self):
        return "Nothing"


@MonadTransformer(Maybe)
def MaybeT(BaseClass):


    @attr.s(frozen=True, repr=False)
    class Transformed(BaseClass):


        def join(self):
            """MaybeT m (MaybeT m a) -> MaybeT m a

            As decompressed:

              m (Maybe (m (Maybe a))) -> m (Maybe a)

            For instance,

            List(Just(List(Just(1), Nothing)), Nothing, Just(List(Nothing, Just(4))))

            -> List(Just(1), Nothing, Nothing, Nothing, Just(4))
            """
            cls = self.__class__
            return Transformed(
                self.decomposed.map(
                    lambda x: x.match(
                        Nothing=lambda: cls.OuterClass.pure(Nothing),
                        Just=lambda x: x.decomposed,
                    )
                ).join()
            )


        # def bind(self, f):
        #     """MaybeT m a -> (a -> MaybeT m b) -> MaybeT m b

        #     In decompressed terms:

        #       m (Maybe a) -> (a -> m (Maybe b)) -> m (Maybe b)

        #     """

        #     mMa = self.decompressed # :: m (Maybe a)

        #     # f :: a -> MaybeT m b
        #     # g :: Maybe a -> m (Maybe b)

        #     g = lambda Ma: Ma.map(f) # :: Maybe (MaybeT m b)


        #     y = self.decomposed.bind(g) # :: m (Maybe b)

        #     return Transformed(y) # :: MaybeT m b


    return Transformed


# class MaybeADT():


#     class Just():
#         __x = attr.ib()

#     @singleton
#     class Nothing():
#         pass

#     # or attrs programmatically

#     Just = case(lambda x: x)
#     Nothing = case(None)


#     def match(self, Just, Nothing):
#         pass


# class LinkedListADT():


#     Empty = case(None)
#     Cons = case(lambda x, xs: (x, xs))
