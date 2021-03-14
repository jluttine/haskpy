from hypothesis import given
import hypothesis.strategies as st

from haskpy.internal import (
    class_function,
    abstract_class_property,
    abstract_class_function,
)
from haskpy.testing import assert_output
from ._semigroup import Semigroup


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

    @class_function
    def sample_monoid_type(cls):
        """Sample a monoid type

        By default, :py:meth:`.Semigroup.sample_semigroup_type` is used. If
        Monoid type requires more constraints Semigroup type, override this
        default implementation.

        """
        return cls.sample_semigroup_type()

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
