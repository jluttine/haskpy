"""A collection of useful simple monoids"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monoid, CommutativeMonoid, Hashable


class _SumMeta(type(CommutativeMonoid), type(Hashable)):


    @property
    def empty(cls):
        return cls(0)


    def sample_type(cls):
        return st.just(st.integers().map(Sum))


@attr.s(frozen=True)
class Sum(CommutativeMonoid, Hashable, metaclass=_SumMeta):


    number = attr.ib()


    def append(self, x):
        return Sum(self.number + x.number)


class _AndMeta(type(CommutativeMonoid), type(Hashable)):


    @property
    def empty(cls):
        return cls(True)


    def sample_type(cls):
        return st.just(st.booleans().map(And))


@attr.s(frozen=True)
class And(CommutativeMonoid, Hashable, metaclass=_AndMeta):


    boolean = attr.ib()


    def append(self, x):
        return And(self.boolean and x.boolean)


class _OrMeta(type(CommutativeMonoid), type(Hashable)):


    @property
    def empty(cls):
        return cls(False)


    def sample_type(cls):
        return st.just(st.booleans().map(Or))


@attr.s(frozen=True)
class Or(CommutativeMonoid, Hashable, metaclass=_OrMeta):


    boolean = attr.ib()


    def append(self, x):
        return Or(self.boolean or x.boolean)


class _StringMeta(type(Monoid), type(Hashable)):


    @property
    def empty(cls):
        return cls("")


    def sample_type(cls):
        return st.just(st.text().map(lambda s: String(s)))


@attr.s(frozen=True, repr=False)
class String(Monoid, Hashable, metaclass=_StringMeta):


    string = attr.ib(converter=str)


    def append(self, s):
        return String(self.string + s.string)


    def __str__(self):
        return self.string


    def __repr__(self):
        return "String({})".format(repr(self.string))
