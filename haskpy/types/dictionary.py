"""Dictionaries

.. autosummary::
   :toctree:

   Dictionary
   lookup

"""

import itertools
import functools
import builtins

import attr
from hypothesis import strategies as st

from haskpy.internal import immutable, class_function, class_property
from haskpy.typeclasses import Apply, Eq, Monoid, Traversable, lift2
from haskpy.types.maybe import Just, Nothing
from haskpy.types.function import function
from haskpy import testing


@immutable(init=False)
class Dictionary(Apply, Eq, Monoid, Traversable):
    """Dictionary type

    .. todo::

        For method ideas, refer to:
        `<https://pursuit.purescript.org/packages/purescript-unordered-collections/0.2.0/docs/Data.HashMap>`_

    """

    __dict = attr.ib()

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, "_Dictionary__dict", dict(*args, **kwargs))
        return

    @class_property
    def empty(cls):
        """Empty dictionary"""
        return cls()

    def append(self, other):
        """Combine two dictionaries

        ::

            Semigroup a => Dictionary a -> Dictionary a -> Dictionary a

        .. note::

            If a key is in both dictionaries, the values are expected to be
            semigroup instances, so that they can be combined. Alternative
            solutions would be to prefer either the first or the second
            dictionary value as done in Haskell and PureScript, so that there
            would be no need to constrain the contained type to be an instance
            of Semigroup. This class provides separate methods
            :py:meth:`.Dictionary.append_first` and
            :py:meth:`.Dictionary.append_second` for those purposes.

        """
        self_keys = set(self.__dict.keys())
        other_keys = set(other.__dict.keys())

        self_only_keys = self_keys.difference(other_keys)
        other_only_keys = other_keys.difference(self_keys)
        both_keys = self_keys.intersection(other_keys)

        return Dictionary(
            {
                key: (
                    self.__dict[key] if c == 1 else
                    other.__dict[key] if c == 2 else
                    self.__dict[key].append(other.__dict[key])
                )
                for (c, key) in itertools.chain(
                        zip(itertools.repeat(1), self_only_keys),
                        zip(itertools.repeat(2), other_only_keys),
                        zip(itertools.repeat(3), both_keys),
                )
            }
        )

    def append_first(self, other):
        """Combine two dictionaries preferring the elements of the first"""
        def get(key):
            try:
                return self.__dict[key]
            except KeyError:
                return other.__dict[key]
        return Dictionary({
            key: get(key)
            for key in set(self.__dict.keys()).union(set(other.__dict.keys()))
        })

    def append_second(self, other):
        """Combine two dictionaries preferring the elements of the second"""
        def get(key):
            try:
                return other.__dict[key]
            except KeyError:
                return self.__dict[key]
        return Dictionary({
            key: get(key)
            for key in set(self.__dict.keys()).union(set(other.__dict.keys()))
        })

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

    # def bind(self, f):
    #     """Dictionary k a -> (a -> Dictionary k b) -> Dictionary k b

    #     When joining values for identical keys, the first (left) dictionary
    #     value is preferred. However, note that it can be random in which order
    #     the dictionaries are joined.

    #     """
    #     return self.map(f).foldl(
    #         append_first,
    #         Dictionary()
    #     )

    def fold_map(self, monoid, f):
        """Monoid m => Dictionary k a -> Monoid -> (a -> m) -> m"""
        xs = builtins.map(f, self.__dict.values())
        return functools.reduce(
            monoid.append,
            xs,
            monoid.empty,
        )

    def foldl(self, combine, initial):
        """Dictionary k a -> (b -> a -> b) -> b -> b"""
        return functools.reduce(
            lambda acc, x: combine(acc)(x),
            self.__dict.values(),
            initial,
        )

    def foldr(self, combine, initial):
        """Dictionary k a -> (a -> b -> b) -> b -> b"""
        return functools.reduce(
            lambda acc, x: combine(x)(acc),
            reversed(self.__dict.values()),
            initial,
        )

    def foldl_with_index(self, combine, initial):
        """Dictionary k a -> (k -> b -> a -> b) -> b -> b"""
        return functools.reduce(
            lambda acc, key_value: combine(key_value[0])(acc)(key_value[1]),
            self.__dict.items(),
            initial,
        )

    def sequence(self, applicative):
        """Applicative f => Dictionary k (f a) -> f (Dictionary k a)"""
        return self.foldl_with_index(
            lambda key: lift2(
                lambda xs: lambda x: xs.append(Dictionary({key: x}))
            ),
            applicative.pure(Dictionary()),
        )

    def lookup(self, key):
        try:
            x = self.__dict[key]
        except KeyError:
            return Nothing
        else:
            return Just(x)

    @class_function
    def singleton(cls, key, value):
        return cls({key: value})

    def insert(self, key, value):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def update(self, f, key):
        raise NotImplementedError()

    def alter(self, f, key):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()

    def values(self):
        raise NotImplementedError()

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
        return st.dictionaries(k, a, max_size=3).map(Dictionary)

    sample_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler(
        testing.sample_hashable_type(),
    )

    sample_foldable_type_constructor = sample_functor_type_constructor

    sample_eq_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_eq_type(),
    )

    sample_semigroup_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
        testing.sample_semigroup_type(),
    )


@function
def lookup(key, d):
    return d[key]


@function
def append_first(x, y):
    return x.append_first(y)


@function
def append_second(x, y):
    return x.append_second(y)
