import hypothesis.strategies as st
from hypothesis import given

from .typeclass import Type
from haskpy.utils import (
    assert_output,
    class_function,
    abstract_function,
    abstract_class_function,
)


class Semigroup(Type):
    """Semigroup typeclass

    Minimal complete definition:

    ..

        append

    For property tests:

    ..

        sample_semigroup_type

    """

    @abstract_function
    def append(self, x):
        """m -> m -> m"""

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_semigroup_type(cls):
        pass

    #
    # Test Semigroup laws
    #

    @class_function
    @given(st.data())
    def test_semigroup_associativity(cls, data):
        """Test semigroup associativity law"""
        # Draw types
        t = data.draw(cls.sample_semigroup_type())

        # Draw values
        x = data.draw(t)
        y = data.draw(t)
        z = data.draw(t)

        cls.assert_semigroup_associativity(x, y, z, data=data)
        return

    @class_function
    @assert_output
    def assert_semigroup_associativity(cls, x, y, z):
        """x <> (y <> z) = (x <> y) <> z"""
        return (
            x.append(y).append(z),
            x.append(y.append(z)),
        )


class Commutative(Semigroup):
    """Semigroup following commutativity law

    This typeclass doesn't add any features nor methods. It only adds a test
    for the commutativity law.

    Minimal complete definition:

    ..

        append

    For property tests:

    ..

        sample_semigroup_type & sample_commutative_type

    """

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_commutative_type(cls):
        pass

    #
    # Test Commutative laws
    #

    @class_function
    @assert_output
    def assert_commutative_commutativity(cls, x, y):
        return (x.append(y), y.append(x))

    @class_function
    @given(st.data())
    def test_commutative_commutativity(cls, data):
        # Draw types
        t = data.draw(cls.sample_commutative_type())

        # Draw values
        x = data.draw(t)
        y = data.draw(t)

        cls.assert_commutative_commutativity(x, y, data=data)
        return


# Semigroup-related functions are defined in function module because of
# circular dependency.
