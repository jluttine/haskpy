import attr

from haskpy.typeclasses.applicative import Applicative
from haskpy.utils import singleton, function


__all__ = ["Just", "Nothing"]


@attr.s(frozen=True, repr=False)
class Just(Applicative):


    value = attr.ib()


    @function
    def map(self, f):
        return Just(f(self.value))


    @function
    def apply_to(self, x):
        return x.map(self.value)


    def __repr__(self):
        return "Just({0})".format(repr(self.value))


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Applicative):


    @function
    def map(self, f):
        return self


    @function
    def apply_to(self, x):
        return self


    def __repr__(self):
        return "Nothing"


@function
def pure(x):
    return Just(x)
