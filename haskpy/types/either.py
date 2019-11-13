import attr
import hypothesis.strategies as st
from hypothesis import given

from haskpy.typeclasses import Monad
from haskpy.utils import sample_type

from haskpy import testing


class _EitherMeta(type(Monad)):


    def pure(cls, x):
        return Right(x)


    def sample_value(cls, a, b):
        return st.one_of(a.map(Left), b.map(Right))


    @st.composite
    def sample_functor_value(draw, cls, b):
        a = draw(testing.sample_type())
        return draw(cls.sample_value(a, b))


@attr.s(frozen=True, repr=False)
class Either(Monad, metaclass=_EitherMeta):


    def match(self, *, Left, Right):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Left(Either):


    __x = attr.ib()


    def match(self, *, Left, Right):
        return Left(self.__x)


    def map(self, f):
        return self


    def apply_to(self, x):
        return self


    def bind(self, f):
        return self


    def __repr__(self):
        return "Left({0})".format(repr(self.__x))


@attr.s(frozen=True, repr=False)
class Right(Either):


    __x = attr.ib()


    def match(self, *, Left, Right):
        return Right(self.__x)


    def map(self, f):
        return Right(f(self.__x))


    def apply_to(self, x):
        return x.map(self.__x)


    def bind(self, f):
        return f(self.__x)


    def __repr__(self):
        return "Right({0})".format(repr(self.__x))
