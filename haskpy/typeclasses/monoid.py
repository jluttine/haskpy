import attr

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
