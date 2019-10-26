import attr
import hypothesis.strategies as st
from hypothesis import given

from haskpy.typeclasses import Monad, Monoid, PatternMatchable
from .monadtransformer import MonadTransformer
from haskpy.utils import singleton


class _MaybeMeta(type(Monad), type(Monoid)):


    @property
    def empty(cls):
        return Nothing


    def pure(cls, x):
        return Just(x)


    @given(st.data())
    def test_semigroup_associativity(cls, data):
        """Test semigroup associativity law"""
        # Need to override the default implementation because we need to have
        # semigroup instance as the encapsulated type, not just some plain
        # values.
        from haskpy.types import List
        cls.assert_semigroup_associativity(
            data.draw(cls.sample(List.sample(st.integers()))),
            data.draw(cls.sample(List.sample(st.integers()))),
            data.draw(cls.sample(List.sample(st.integers()))),
        )
        return


    @st.composite
    def sample(draw, cls, elements):
        b = draw(st.booleans())
        return (
            Just(draw(elements)) if b else
            Nothing
        )


# Some thoughts on design: One could implement all the methods (except match)
# in Maybe class by using the match method to choose the implementation. But
# this would be just clumsy and add overhead. Class inheritance is a Pythonic
# way of choosing the correct method implementation. Also, Just needs to
# support equality testing, so that's also easy to achieve by making it a
# class.


@attr.s(frozen=True, repr=False)
class Maybe(Monad, Monoid, PatternMatchable, metaclass=_MaybeMeta):
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


    return Transformed
