"""A collection of useful simple monoids"""

import attr

from haskpy.typeclasses import Monoid


class _SumMeta(type(Monoid)):


    @property
    def empty(cls):
        return cls(0)


@attr.s(frozen=True)
class Sum(Monoid, metaclass=_SumMeta):


    number = attr.ib()


    def append(self, x):
        return Sum(self.number + x.number)


class _AndMeta(type(Monoid)):


    @property
    def empty(cls):
        return cls(True)


@attr.s(frozen=True)
class And(Monoid, metaclass=_AndMeta):


    boolean = attr.ib()


    def append(self, x):
        return And(self.boolean and x.boolean)


class _OrMeta(type(Monoid)):


    @property
    def empty(cls):
        return cls(False)


@attr.s(frozen=True)
class Or(Monoid, metaclass=_OrMeta):


    boolean = attr.ib()


    def append(self, x):
        return Or(self.boolean or x.boolean)
