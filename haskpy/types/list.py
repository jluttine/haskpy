import attr

from haskpy.typeclasses import Monad


class ListMeta(type(Monad)):


    def pure(cls, x):
        """a -> List a"""
        return cls(x)


    def from_iter(cls, xs):
        """Iterable f => f a -> List a"""
        return cls(*xs)


@attr.s(frozen=True, repr=False, init=False)
class List(Monad, metaclass=ListMeta):


    __xs = attr.ib(converter=tuple)


    def __init__(self, *xs):
        object.__setattr__(self, "_List__xs", tuple(xs))
        return


    def map(self, f):
        """List a -> (a -> b) -> List b"""
        return List(*(f(x) for x in self.__xs))


    def apply(self, fs):
        """List a -> List (a -> b) -> List b"""
        return List(*(y for f in fs.__xs for y in self.map(f).__xs))


    def bind(self, f):
        """List a -> (a -> List b) -> List b"""
        return List(*(y for ys in self.map(f).__xs for y in ys.__xs))


    def __repr__(self):
        return "List{}".format(repr(self.__xs))
