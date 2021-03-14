"""Dictionaries

.. autosummary::
   :toctree:

   Dictionary

"""

import attr
from hypothesis import strategies as st

from haskpy.internal import immutable, class_function
from haskpy.typeclasses import Apply, Eq
from haskpy.types.maybe import Just, Nothing
from haskpy.types.function import function
from haskpy import testing


@immutable(init=False)
class Dictionary(Apply, Eq):
    """Dictionary type"""

    __dict = attr.ib()

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, "_Dictionary__dict", dict(*args, **kwargs))
        return

    def map(self, f):
        """Apply a function to each value in the dictionary

        ::

            Dictionary k a -> (a -> b) -> Dictionary k b

        """
        return Dictionary({
            key: f(value)
            for (key, value) in self.__dict.items()
        })

    def apply(self, f):
        """Apply a dictionary of functions to a dictionary of values

        ::

            Dictionary k a -> Dictionary k (a -> b) -> Dictionary k b

        .. note::

            The resulting dictionary will have only such keys that are in both
            of the input dictionaries.

        """
        self_keys = set(self.__dict.keys())
        f_keys = set(f.__dict.keys())
        keys = self_keys.intersection(f_keys)
        return Dictionary({
            key: f.__dict[key](self.__dict[key])
            for key in keys
        })

    def lookup(self, key):
        try:
            x = self.__dict[key]
        except KeyError:
            return Nothing
        else:
            return Just(x)

    def __getitem__(self, key):
        return self.lookup(key)

    def __repr__(self):
        return "Dictionary({})".format(repr(self.__dict))

    def __eq__(self, other):
        return self.__dict == other.__dict

    def __eq_test__(self, other, data=None):
        return (
            self.__dict.keys() == other.__dict.keys() and
            all(
                testing.eq_test(self.__dict[key], other.__dict[key], data)
                for key in self.__dict.keys()
            )
        )

    @class_function
    def sample_value(cls, k, a):
        return st.dictionaries(k, a).map(Dictionary)

    sample_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler(
        testing.sample_hashable_type(),
    )
    sample_apply_type_constructor = sample_functor_type_constructor

    sample_eq_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_eq_type(),
    )


@function
def lookup(key, d):
    return d[key]
