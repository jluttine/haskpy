import attr

from haskpy.typeclasses.applicative import Applicative
from haskpy.utils import singleton, function


__all__ = ["Just", "Nothing"]


@attr.s(frozen=True)
class Maybe(Applicative):


    @classmethod
    def pure(cls, x):
        return Just(x)


    def match(self, Just, Nothing):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Just(Maybe):


    value = attr.ib()


    @classmethod
    def pure(cls, x):
        return


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
    def map(self, f):
        return self


    @function
    def apply_to(self, x):
        return self


    def match(self, Just, Nothing):
        return Nothing()


    def __repr__(self):
        return "Nothing"
