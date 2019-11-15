"""A collection of useful simple monoids"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monoid, CommutativeMonoid, Hashable
from haskpy import testing
from haskpy.utils import identity


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


class _EndoMeta(type(Monoid)):


    @property
    def empty(cls):
        return cls(identity)


    def sample_type(cls):
        return testing.sample_hashable_type().map(
            lambda a: testing.sample_function(a).map(lambda f: Endo(f))
        )


@attr.s(frozen=True, repr=False, cmp=False)
class Endo(Monoid, metaclass=_EndoMeta):
    """Endofunction monoid (a -> a)"""


    app_endo = attr.ib()


    def append(self, f):
        # Append by composing
        return Endo(lambda a: self.app_endo(f.app_endo(a)))


    def __repr__(self):
        return "Endo({})".format(self.app_endo)


    def __test_eq__(self, other, data, input_strategy=st.integers()):
        x = data.draw(input_strategy)
        return self.app_endo(x) == other.app_endo(x)
