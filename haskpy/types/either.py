import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monad
from haskpy.utils import class_function, immutable

from haskpy import testing


@immutable
class Either(Monad):

    def match(self, *, Left, Right):
        raise NotImplementedError()

    @class_function
    def pure(cls, x):
        return Right(x)

    @class_function
    def sample_value(cls, a, b):
        return st.one_of(a.map(Left), b.map(Right))

    @class_function
    @st.composite
    def sample_functor_value(draw, cls, b):
        a = draw(testing.sample_type())
        return draw(cls.sample_value(a, b))


@immutable
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


@immutable
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
