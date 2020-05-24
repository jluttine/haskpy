"""A collection of useful simple monoids"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monoid, CommutativeMonoid, Hashable, Eq
from haskpy import testing
from haskpy.utils import (
    identity,
    class_property,
    class_function,
    immutable,
    eq_test,
)


@immutable
class Sum(CommutativeMonoid, Hashable, Eq):

    number = attr.ib()

    @class_property
    def empty(cls):
        return cls(0)

    def append(self, x):
        return Sum(self.number + x.number)

    def __eq__(self, other):
        return self.number == other.number

    @class_function
    def sample_type(cls):
        return st.just(st.integers().map(Sum))


@immutable
class And(CommutativeMonoid, Hashable, Eq):

    boolean = attr.ib()

    @class_property
    def empty(cls):
        return cls(True)

    def append(self, x):
        return And(self.boolean and x.boolean)

    def __eq__(self, other):
        return self.boolean == other.boolean

    @class_function
    def sample_type(cls):
        return st.just(st.booleans().map(And))


@immutable
class Or(CommutativeMonoid, Hashable, Eq):

    boolean = attr.ib()

    @class_property
    def empty(cls):
        return cls(False)

    def append(self, x):
        return Or(self.boolean or x.boolean)

    def __eq__(self, other):
        return self.boolean == other.boolean

    @class_function
    def sample_type(cls):
        return st.just(st.booleans().map(Or))


@immutable
class String(Monoid, Hashable, Eq):

    string = attr.ib(converter=str)

    @class_property
    def empty(cls):
        return cls("")

    def append(self, s):
        return String(self.string + s.string)

    def __eq__(self, other):
        return self.string == other.string

    def __str__(self):
        return self.string

    def __repr__(self):
        return "String({})".format(repr(self.string))

    @class_function
    def sample_type(cls):
        return st.just(st.text().map(lambda s: String(s)))


@immutable
class Endo(Monoid):
    """Endofunction monoid (a -> a)"""

    app_endo = attr.ib()

    @class_property
    def empty(cls):
        return cls(identity)

    def append(self, f):
        # Append by composing
        return Endo(lambda a: self.app_endo(f.app_endo(a)))

    def __repr__(self):
        return "Endo({})".format(self.app_endo)

    def __eq_test__(self, other, data, input_strategy=st.integers()):
        x = data.draw(input_strategy)
        return eq_test(self.app_endo(x), other.app_endo(x), data)

    @class_function
    def sample_type(cls):
        return testing.sample_hashable_type().map(
            lambda a: testing.sample_function(a).map(lambda f: Endo(f))
        )
