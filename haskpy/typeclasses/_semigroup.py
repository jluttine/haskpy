import hypothesis.strategies as st
from hypothesis import given

from .typeclass import Type
from haskpy.testing import assert_output
from haskpy.internal import class_function, abstract_function


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

    def __add__(self, other):
        """Append two monoids

        Using ``+`` operator to append two monoid values seems natural because
        that's what Python is doing by default because lists are concatenated
        with ``+``.

        """
        return self.append(other)

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_semigroup_type(cls):
        """Sample a semigroup type

        By default, :py:meth:`.Type.sample_type` is used. If Semigroup type
        requires some constraints, override this default implementation.

        """
        return cls.sample_type()

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

    @class_function
    @given(st.data())
    def test_semigroup_append_and_add(cls, data):
        # Draw types
        t = data.draw(cls.sample_semigroup_type())

        # Draw values
        x = data.draw(t)
        y = data.draw(t)

        cls.assert_semigroup_append_and_add(x, y, data=data)
        return

    @class_function
    @assert_output
    def assert_semigroup_append_and_add(cls, x, y):
        from .semigroup import append
        return (
            x.append(y),
            x + y,
            append(x, y)
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

    @class_function
    def sample_commutative_type(cls):
        """Sample a commutative type

        By default, :py:meth:`.Semigroup.sample_semigroup_type` is used. If
        Commutative type requires more constraints Semigroup type, override
        this default implementation.

        """
        return cls.sample_semigroup_type()

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
