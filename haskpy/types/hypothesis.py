"""Thin wrappers for some Hypothesis strategies

.. note::

    These classes aren't any real data types. They just wrap Hypothesis
    strategies into classes so they can be used in tests consistently.

"""

import hypothesis.strategies as st

from haskpy.typeclasses import Type, Hashable
from haskpy import testing


class _HypothesisListMeta(type(Type)):


    def sample_type(cls):
        a = testing.sample_type()
        return a.map(st.lists)


class HypothesisList(Type, metaclass=_HypothesisListMeta):
    pass



class _HypothesisIntegerMeta(type(Hashable)):


    def sample_type(cls):
        return st.just(st.integers())


class HypothesisInteger(Hashable, metaclass=_HypothesisIntegerMeta):
    pass
