import attr
import hypothesis.strategies as st
from hypothesis import given

from .typeclass import Type
from haskpy.utils import assert_output


class _SemigroupMeta(type(Type)):


    def sample_semigroup_type(draw, cls):
        # By default, assume the class is a concrete type or that any random
        # types for the type constructor make the concrete type semigroup.
        return cls.sample_type()


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


    @assert_output
    def assert_semigroup_associativity(cls, x, y, z):
        """x <> (y <> z) = (x <> y) <> z"""
        return (
            x.append(y).append(z),
            x.append(y.append(z)),
        )


class Semigroup(Type, metaclass=_SemigroupMeta):
    """Semigroup typeclass

    Minimal complete definition:

    - ``append``

    """


    def append(self, x):
        """m -> m -> m"""
        raise NotImplementedError()


class _CommutativeMeta(type(Semigroup)):


    def sample_commutative_type(cls):
        # By default, assume the class is a concrete type or that the
        # commutative-property of the type constructor doesn't depend on the
        # contained type.
        return cls.sample_type()


    @assert_output
    def assert_commutative_commutativity(cls, x, y):
        return (x.append(y), y.append(x))


    @given(st.data())
    def test_commutative_commutativity(cls, data):
        # Draw types
        t = data.draw(cls.sample_commutative_type())

        # Draw values
        x = data.draw(t)
        y = data.draw(t)

        cls.assert_commutative_commutativity(x, y)
        return


class Commutative(Semigroup, metaclass=_CommutativeMeta):
    """Semigroup following commutativity law

    This typeclass doesn't add any features nor methods. It only adds a test
    for the commutativity law.

    Minimal complete definition:

    - ``append``

    """


# Semigroup-related functions are defined in function module because of
# circular dependency.
