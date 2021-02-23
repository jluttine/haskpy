from hypothesis import given
import hypothesis.strategies as st

from haskpy.utils import (
    assert_output,
    class_function,
    abstract_class_property,
    abstract_class_function,
)
from .semigroup import Semigroup, Commutative


class Monoid(Semigroup):
    """Monoid typeclass

    Minimal complete definition:

    ..

        empty & append

    For property tests:

    ..

        sample_monoid_type & sample_semigroup_type

    """

    @abstract_class_property
    def empty(cls):
        """Identity element for the monoid"""

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

    @abstract_class_function
    def sample_monoid_type(cls):
        pass


# Monoid-related functions are defined in function module because of circular
# dependency.
