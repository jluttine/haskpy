from hypothesis import given
import hypothesis.strategies as st

from haskpy.utils import assert_output, class_function, abstract_class_property
from .semigroup import Semigroup, Commutative


class Monoid(Semigroup):
    """Monoid typeclass

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """

    @abstract_class_property
    def empty(cls):
        """Identity element for the monoid"""

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_semigroup_type(cls):
        return cls.sample_monoid_type()

    @class_function
    def sample_monoid_type(cls):
        # By default, assume the class is a concrete type or that the
        # monoid-property of the type constructor doesn't depend on the
        # contained type.
        return cls.sample_type()

    #
    # Test Monoid laws
    #

    @class_function
    @given(st.data())
    def test_monoid_identity(cls, data):
        """Test monoid identity law"""
        # Draw types
        t = data.draw(cls.sample_monoid_type())

        # Draw values
        x = data.draw(t)

        cls.assert_monoid_identity(x, data=data)
        return

    @class_function
    @assert_output
    def assert_monoid_identity(cls, x):
        return (
            x,
            x.append(cls.empty),
            cls.empty.append(x),
        )


class CommutativeMonoid(Commutative, Monoid):
    """Monoid following the commutativity law

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """
    pass


# Monoid-related functions are defined in function module because of circular
# dependency.
