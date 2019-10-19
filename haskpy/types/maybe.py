import attr

from haskpy.typeclasses import Monad, PatternMatchable
from haskpy.utils import singleton
from haskpy.function import function


__all__ = ["Just", "Nothing"]


@attr.s(frozen=True)
class Maybe(Monad, PatternMatchable):


    @classmethod
    def pure(cls, x):
        return Just(x)


    def match(self, Just, Nothing):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Just(Maybe):


    value = attr.ib()


    def bind(self, f):
        return f(self.value)


    def map(self, f):
        return Just(f(self.value))


    def apply_to(self, x):
        return x.map(self.value)


    def match(self, Just, Nothing):
        return Just(self.value)


    def __repr__(self):
        return "Just({0})".format(repr(self.value))


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Maybe):


    def bind(self, f):
        return Nothing


    def map(self, f):
        return Nothing


    def apply_to(self, x):
        return Nothing


    def match(self, Just, Nothing):
        return Nothing()


    def __repr__(self):
        return "Nothing"
