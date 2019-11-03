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


    def sample_semigroup(cls, **kwargs):
        return cls.sample_monoid(**kwargs)


    def sample_monoid(cls, **kwargs):
        # By default, assume the class is a concrete type or that the
        # monoid-property of the type constructor doesn't depend on the
        # contained type.
        return cls.sample(**kwargs)


    @given(st.data())
    def test_monoid_identity(cls, data):
        cls.assert_monoid_identity(
            data.draw(cls.sample_monoid()),
            data=data
        )
        return


    @assert_output
    def assert_monoid_identity(cls, x):
        return (
            x,
            x.append(cls.empty),
            cls.empty.append(x),
        )


@attr.s(frozen=True)
class Monoid(Semigroup, metaclass=_MonoidMeta):
    """Monoid typeclass

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """
    pass



class _CommutativeMonoidMeta(type(Monoid), type(Commutative)):
    pass


@attr.s(frozen=True)
class CommutativeMonoid(Monoid, Commutative, metaclass=_CommutativeMonoidMeta):
    """Monoid following the commutativity law

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """
    pass


# Monoid-related functions are defined in function module because of circular
# dependency.
