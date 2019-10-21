import attr

from haskpy.typeclasses import Monoid


class _StringMeta(type(Monoid)):


    @property
    def empty(cls):
        return cls("")


@attr.s(frozen=True, repr=False)
class String(Monoid, metaclass=_StringMeta):


    __s = attr.ib()


    def append(self, s):
        return String(self.__s + s.__s)


    def __repr__(self):
        return "String({})".format(repr(self.__s))
