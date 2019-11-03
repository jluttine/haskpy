import attr
import hypothesis.strategies as st
from hypothesis import given

from .typeclass import Type


class _SemigroupMeta(type(Type)):


    def sample_semigroup(draw, cls):
        # By default, assume the class is a concrete type or that any random
        # types for the type constructor make the concrete type semigroup.
        return cls.sample()


    @given(st.data())
    def test_semigroup_associativity(cls, data):
        """Test semigroup associativity law"""
        cls.assert_semigroup_associativity(
            # NOTE: By using size argument instead of sampling independently,
            # we get the same concrete type even with type constructors that
            # can give many concrete types.
            *data.draw(cls.sample_semigroup(size=3)),
        )
        return


    def assert_semigroup_associativity(cls, x, y, z):
        """x <> (y <> z) = (x <> y) <> z"""
        assert x.append(y).append(z) == x.append(y.append(z))
        return


@attr.s(frozen=True)
class Semigroup(Type, metaclass=_SemigroupMeta):
    """Semigroup typeclass

    Minimal complete definition:

    - ``append``

    """


    def append(self, x):
        """m -> m -> m"""
        raise NotImplementedError()


class _CommutativeMeta(type(Semigroup)):


    @st.composite
    def sample_commutative(draw, cls, **kwargs):
        return draw(cls.sample(**kwargs))


    def assert_commutative_commutativity(cls, x, y):
        assert x.append(y) == y.append(x)
        return


    @given(st.data())
    def test_commutative_commutativity(cls, data):
        (x, y) = data.draw(cls.sample_commutative(size=2))
        cls.assert_commutative_commutativity(x, y)
        return


@attr.s(frozen=True)
class Commutative(Semigroup, metaclass=_CommutativeMeta):
    """Semigroup following commutativity law

    This typeclass doesn't add any features nor methods. It only adds a test
    for the commutativity law.

    Minimal complete definition:

    - ``append``

    """


# Semigroup-related functions are defined in function module because of
# circular dependency.
