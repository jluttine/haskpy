import attr

from haskpy.typeclasses import Monad
from haskpy.utils import singleton, function


__all__ = ["Just", "Nothing"]


@attr.s(frozen=True)
class Maybe(Monad):


    @classmethod
    def pure(cls, x):
        return Just(x)


    def match(self, Just, Nothing):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Just(Maybe):


    value = attr.ib()


    @function
    def bind(self, f):
        return f(self.value)


    @function
    def map(self, f):
        return Just(f(self.value))


    @function
    def apply_to(self, x):
        return x.map(self.value)


    def match(self, Just, Nothing):
        return Just(self.value)


    def __repr__(self):
        return "Just({0})".format(repr(self.value))


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Maybe):


    @function
    def bind(self, f):
        return Nothing


    @function
    def map(self, f):
        return Nothing


    @function
    def apply_to(self, x):
        return Nothing


    def match(self, Just, Nothing):
        return Nothing()


    def __repr__(self):
        return "Nothing"
