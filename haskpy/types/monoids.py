"""Simple monoids

.. autosummary::
   :toctree:

   Sum
   All
   Any
   String
   Endo

.. todo::

   ``Product``

"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monoid, Commutative, Hashable
from haskpy.utils import identity
from haskpy.internal import (
    class_property,
    class_function,
    immutable,
)
from haskpy.testing import eq_test
from haskpy import testing


@immutable
class Sum(Commutative, Monoid, Hashable):
    """Sum monoid"""

    number = attr.ib()

    @class_property
    def empty(cls):
        return cls(0)

    def append(self, x):
        return Sum(self.number + x.number)

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

    def __repr__(self):
        return "Sum({})".format(repr(self.number))

    @class_function
    def sample_value(cls):
        return st.integers().map(Sum)

    sample_type = testing.create_type_sampler()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_commutative_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


@immutable
class All(Commutative, Monoid, Hashable):
    """All monoid"""

    boolean = attr.ib()

    @class_property
    def empty(cls):
        return cls(True)

    def append(self, x):
        return All(self.boolean and x.boolean)

    def __eq__(self, other):
        return self.boolean == other.boolean

    def __hash__(self):
        return hash(self.boolean)

    def __repr__(self):
        return "All({})".format(repr(self.boolean))

    @class_function
    def sample_value(cls):
        return st.booleans().map(All)

    sample_type = testing.create_type_sampler()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_commutative_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


@immutable
class Any(Commutative, Monoid, Hashable):
    """Any monoid"""

    boolean = attr.ib()

    @class_property
    def empty(cls):
        return cls(False)

    def append(self, x):
        return Any(self.boolean or x.boolean)

    def __eq__(self, other):
        return self.boolean == other.boolean

    def __hash__(self):
        return hash(self.boolean)

    def __repr__(self):
        return "Any({})".format(repr(self.boolean))

    @class_function
    def sample_value(cls):
        return st.booleans().map(Any)

    sample_type = testing.create_type_sampler()
    sample_eq_type = sample_type
    sample_semigroup_type = sample_type
    sample_commutative_type = sample_type
    sample_monoid_type = sample_type
    sample_hashable_type = sample_type


@immutable
class String(Monoid, Hashable):
    """String monoid"""

    string = attr.ib(converter=str)

    @class_property
    def empty(cls):
        return cls("")

    def append(self, s):
        return String(self.string + s.string)

    def __eq__(self, other):
        return self.string == other.string

    def __hash__(self):
        return hash(self.string)

    def __str__(self):
        return self.string

    def __repr__(self):
        return "String({})".format(repr(self.string))

    @class_function
    def sample_value(cls):
        return st.text().map(lambda s: String(s))

    sample_type = testing.create_type_sampler()
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

    sample_type = testing.create_type_sampler(
        testing.sample_eq_type(),
    )
    sample_semigroup_type = sample_type
    sample_monoid_type = sample_type
