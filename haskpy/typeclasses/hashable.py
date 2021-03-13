"""Hashability for types

.. autosummary::
   :toctree:

   Hashable

"""

from hypothesis import given, strategies as st

from haskpy.typeclasses.equality import Eq
from haskpy.typeclasses.typeclass import Type
from haskpy.internal import (
    abstract_class_function,
    abstract_function,
    class_function,
)
from haskpy import testing


class Hashable(Type):
    """Hashable typeclass

    Minimal complete definition::

        __hash__


    """

    @abstract_function
    def __hash__(self):
        pass

    @abstract_class_function
    def sample_hashable_type(cls):
        pass

    @class_function
    def assert_hashable_equality(cls, x, y):
        if not issubclass(cls, Eq):
            raise TypeError(
                "No support Hashable instance that is not Eq instance"
            )
        assert hash(x) == hash(y) if x == y else True
        return

    @class_function
    @given(st.data())
    def test_hashable_equality(cls, data):
        """Test that hash is equal for equal values

        .. note::


        """

        import pytest
        if not issubclass(cls, Eq):
            # Not sure if Hashable should be a subclass of Eq or not. It
            # shouldn't because, for instance, functions could have hash
            # instance (e.g., hashing of functions of type Int -> Int could
            # just calculate the hash of the output for some fixed integer
            # input.) However, we cannot check this law if they aren't
            # instances of Eq.
            #
            # We cannot use the stochastic eq_test here because it cannot say
            # for sure if the values are equal or not. It can only be certain
            # when it detects they are inequal. But when it thinks the values
            # are equal, they could still be inequal. So, this law cannot be
            # checked with that.
            pytest.skip("{} not an instance of Eq".format(cls.__name__))

        a = data.draw(testing.sample_hashable_type())

        x = data.draw(a)
        y = data.draw(a)

        cls.assert_hashable_equality(x, y)
        return
