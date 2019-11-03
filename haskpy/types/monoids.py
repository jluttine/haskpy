"""A collection of useful simple monoids"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monoid, CommutativeMonoid


class _SumMeta(type(CommutativeMonoid)):


    @property
    def empty(cls):
        return cls(0)


    def sample(cls):
        return st.integers().map(Sum)


@attr.s(frozen=True)
class Sum(CommutativeMonoid, metaclass=_SumMeta):


    number = attr.ib()


    def append(self, x):
        return Sum(self.number + x.number)


class _AndMeta(type(CommutativeMonoid)):


    @property
    def empty(cls):
        return cls(True)


    def sample(cls):
        return st.booleans().map(And)


@attr.s(frozen=True)
class And(CommutativeMonoid, metaclass=_AndMeta):


    boolean = attr.ib()


    def append(self, x):
        return And(self.boolean and x.boolean)


class _OrMeta(type(CommutativeMonoid)):


    @property
    def empty(cls):
        return cls(False)


    def sample(cls):
        return st.booleans().map(Or)


@attr.s(frozen=True)
class Or(CommutativeMonoid, metaclass=_OrMeta):


    boolean = attr.ib()


    def append(self, x):
        return Or(self.boolean or x.boolean)


class _StringMeta(type(Monoid)):


    @property
    def empty(cls):
        return cls("")


    def sample(cls):
        return st.characters().map(String)


@attr.s(frozen=True, repr=False)
class String(Monoid, metaclass=_StringMeta):


    string = attr.ib(converter=str)


    def append(self, s):
        return String(self.string + s.string)


    def __str__(self):
        return self.string


    def __repr__(self):
        return "String({})".format(self.string)
