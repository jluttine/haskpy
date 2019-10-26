import attr
import hypothesis.strategies as st
from hypothesis import given

from .typeclass import TypeclassMeta


class _SemigroupMeta(TypeclassMeta):


    @given(st.data())
    def test_semigroup_associativity(cls, data):
        """Test semigroup associativity law"""
        cls.assert_semigroup_associativity(
            data.draw(cls.sample(st.integers())),
            data.draw(cls.sample(st.integers())),
            data.draw(cls.sample(st.integers())),
        )
        return


    def assert_semigroup_associativity(cls, x, y, z):
        """x <> (y <> z) = (x <> y) <> z"""
        assert x.append(y).append(z) == x.append(y.append(z))
        return


@attr.s(frozen=True)
class Semigroup(metaclass=_SemigroupMeta):
    """Semigroup typeclass

    Minimal complete definition:

    - ``append``

    """


    def append(self, x):
        """m -> m -> m"""
        raise NotImplementedError()


# Semigroup-related functions are defined in function module because of
# circular dependency.
