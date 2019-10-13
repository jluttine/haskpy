import attr

from haskpy.utils import constructor, function
from haskpy.typeclasses import Applicative


__all__ = ["List"]


@constructor(lambda init, *xs: init(xs))
@attr.s(frozen=True, repr=False)
class List(Applicative):


    __xs = attr.ib(converter=tuple)


    @function
    def map(self, f):
        return List(*(f(x) for x in self.__xs))


    @function
    def __repr__(self):
        return "List{0}".format(repr(self.__xs))
