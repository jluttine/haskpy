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


    def length(self):
        return 1


    def to_iter(self):
        yield from (self.__x,)


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


    def length(self):
        return 0


    def to_iter(self):
        yield from ()


    def __repr__(self):
        return "Nothing"


def MaybeT(M):
    """m (Maybe a) -> MaybeT m a"""


    # NOTE: It might be tempting to use Compose as a basis for this kind of
    # Monad transformers. Indeed, it seems like these are just monadic
    # extensions to the composition that can be written only for Applicatives
    # in generic form. However, that is not the case. See an example in
    # test_maybe.py on how MaybeT isn't a monadic extension of Compose but
    # rather its Applicative instance is different from that of Compose. This
    # is rather interesting as it's a common misconception that the common
    # monad transformers are monadic extensions of Compose. Even "Learn Haskell
    # programming from first principles" introduces monad transformers in such
    # a way that it leads to that kind of understanding.


    class _MaybeMMeta(type(Monad)):


        def pure(cls, x):
            """a -> MaybeT m a"""
            return cls(M.pure(Maybe.pure(x)))


        def sample_value(cls, a):
            return M.sample_value(Maybe.sample_value(a)).map(cls)


        def __repr__(cls):
            return "MaybeT({})".format(repr(M))


    @attr.s(frozen=True, repr=False)
    class MaybeM(Monad, metaclass=_MaybeMMeta):


        # The attribute name may sound weird but it makes sense once you
        # understand that this indeed is the not-yet-composed variable and if
        # you want to decompose a composed variable you get it by x.decomposed.
        # Thus, there's no need to write a simple function to just return this
        # attribute, just use this directly.
        decomposed = attr.ib()


        def bind(self, f):
            """MaybeT m a -> (a -> MaybeT m b) -> MaybeT m b

            In decompressed terms:

              m (Maybe a) -> (a -> m (Maybe b)) -> m (Maybe b)

            """

            # :: m (Maybe a)
            mMa = self.decomposed

            # :: Maybe a -> m (Maybe b)
            g = lambda Ma: Ma.match(
                Nothing=lambda: M.pure(Nothing),
                Just=lambda x: f(x).decomposed,
            )

            # :: MaybeT m b
            return MaybeM(mMa.bind(g))


        def __repr__(self):
            return "{0}({1})".format(repr(MaybeM), repr(self.decomposed))


    return MaybeM
