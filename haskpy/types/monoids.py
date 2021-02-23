"""A collection of useful simple monoids"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monoid, Commutative, Hashable, Eq
from haskpy import testing
from haskpy.utils import (
    identity,
    class_property,
    class_function,
    immutable,
    eq_test,
    concrete_type,
)


@immutable
class Sum(Commutative, Monoid, Hashable, Eq):

    number = attr.ib()

    @class_property
    def empty(cls):
        return cls(0)

    def append(self, x):
        return Sum(self.number + x.number)

    def __eq__(self, other):
        return self.number == other.number

    def __repr__(self):
        return "Sum({})".format(repr(self.number))

    @class_function
    def sample_value(cls):
        return st.integers().map(Sum)

    sample_type = testing.sample_type_from_value()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_commutative_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


@immutable
class And(Commutative, Monoid, Hashable, Eq):

    boolean = attr.ib()

    @class_property
    def empty(cls):
        return cls(True)

    def append(self, x):
        return And(self.boolean and x.boolean)

    def __eq__(self, other):
        return self.boolean == other.boolean

    def __repr__(self):
        return "And({})".format(repr(self.boolean))

    @class_function
    def sample_value(cls):
        return st.booleans().map(And)

    sample_type = testing.sample_type_from_value()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_commutative_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


@immutable
class Or(Commutative, Monoid, Hashable, Eq):

    boolean = attr.ib()

    @class_property
    def empty(cls):
        return cls(False)

    def append(self, x):
        return Or(self.boolean or x.boolean)

    def __eq__(self, other):
        return self.boolean == other.boolean

    def __repr__(self):
        return "Or({})".format(repr(self.boolean))

    @class_function
    def sample_value(cls):
        return st.booleans().map(Or)

    sample_type = testing.sample_type_from_value()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_commutative_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


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
    def sample_value(cls):
        return st.text().map(lambda s: String(s))

    sample_type = testing.sample_type_from_value()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


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
    def sample_value(cls, a):
        return testing.sample_function(a).map(lambda f: Endo(f))

    sample_type = testing.sample_type_from_value(
        testing.sample_eq_type(),
    )
    sample_semigroup_type = sample_type
    sample_monoid_type = sample_type
