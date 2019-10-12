import attr

from haskpy.utils import constructor
from haskpy.typeclasses import Applicative
from haskpy.function import Function


__all__ = ["List"]


@constructor(lambda init, *xs: init(xs))
@attr.s(frozen=True, repr=False)
class List(Applicative):


    __xs = attr.ib(converter=tuple)


    @Function
    def map(self, f):
        return List(*(f(x) for x in self.__xs))


    @Function
    def __repr__(self):
        return "List{0}".format(repr(self.__xs))
