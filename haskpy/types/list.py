import attr

from haskpy.utils import function
from haskpy.typeclasses import Applicative


__all__ = ["List"]


@attr.s(frozen=True, repr=False, init=False)
class List(Applicative):


    xs = attr.ib(converter=tuple)


    def __init__(self, *xs):
        object.__setattr__(self, "xs", tuple(xs))
        return


    @classmethod
    def pure(cls, x):
        return cls(x)


    @function
    def map(self, f):
        return List(*(f(x) for x in self.xs))


    def __repr__(self):
        return "List{0}".format(repr(self.xs))
