import attr
from hypothesis import given
import hypothesis.strategies as st

from haskpy.utils import assert_output
from .semigroup import Semigroup, Commutative


class _MonoidMeta(type(Semigroup)):


    @property
    def empty(cls):
        raise NotImplementedError()


    def fold(cls, xs):
        return xs.fold(cls)


    def fold_map(cls, xs, f):
        return xs.fold_map(cls, f)


    def sample_semigroup_type(cls):
        return cls.sample_monoid_type()


    def sample_monoid_type(cls):
        # By default, assume the class is a concrete type or that the
        # monoid-property of the type constructor doesn't depend on the
        # contained type.
        return cls.sample_type()


    @given(st.data())
    def test_monoid_identity(cls, data):
        # Draw types
        t = data.draw(cls.sample_monoid_type())

        # Draw values
        x = data.draw(t)

        cls.assert_monoid_identity(x, data=data)
        return


    @assert_output
    def assert_monoid_identity(cls, x):
        return (
            x,
            x.append(cls.empty),
            cls.empty.append(x),
        )


class Monoid(Semigroup, metaclass=_MonoidMeta):
    """Monoid typeclass

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """
    pass



class _CommutativeMonoidMeta(type(Commutative), type(Monoid)):
    pass


class CommutativeMonoid(Commutative, Monoid, metaclass=_CommutativeMonoidMeta):
    """Monoid following the commutativity law

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """
    pass


# Monoid-related functions are defined in function module because of circular
# dependency.
