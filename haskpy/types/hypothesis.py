"""Thin wrappers for some Hypothesis strategies

.. note::

    These classes aren't any real data types. They just wrap Hypothesis
    strategies into classes so they can be used in tests consistently.

"""

import hypothesis.strategies as st

from haskpy.typeclasses import Eq, Hashable
from haskpy import testing
from haskpy.utils import class_function


class HypothesisList(Eq, Hashable):

    @class_function
    def sample_type(cls):
        a = testing.sample_type()
        return a.map(st.lists)

    @class_function
    def sample_hashable_type(cls):
        a = testing.sample_hashable_type()
        return a.map(st.lists)

    @class_function
    def sample_eq_type(cls):
        a = testing.sample_eq_type()
        return a.map(st.lists)


class HypothesisInteger(Eq, Hashable):

    @class_function
    def sample_type(cls):
        return st.just(st.integers())

    sample_hashable_type = sample_type
    sample_eq_type = sample_type
