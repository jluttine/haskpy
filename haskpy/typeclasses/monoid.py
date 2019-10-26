import attr
from hypothesis import given
import hypothesis.strategies as st

from .semigroup import Semigroup
from .typeclass import TypeclassMeta


class _MonoidMeta(type(Semigroup)):


    @property
    def empty(cls):
        raise NotImplementedError()


    def fold(cls, xs):
        return xs.fold(cls)


    def fold_map(cls, xs, f):
        return xs.fold_map(cls, f)


    @given(st.data())
    def test_monoid_identity(cls, data):
        cls.assert_monoid_identity(
            data.draw(cls.sample(st.integers()))
        )
        cls.assert_monoid_identity(
            data.draw(cls.sample(cls.sample(st.integers())))
        )
        return


    def assert_monoid_identity(cls, x):
        assert x.append(cls.empty) == x == cls.empty.append(x)
        return


@attr.s(frozen=True)
class Monoid(Semigroup, metaclass=_MonoidMeta):
    """Monoid typeclass

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """
    pass


# Monoid-related functions are defined in function module because of circular
# dependency.
