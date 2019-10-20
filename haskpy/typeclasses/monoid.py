import attr

from .typeclass import TypeclassMeta


class _MonoidMeta(TypeclassMeta):


    @property
    def empty(cls):
        raise NotImplementedError()


@attr.s(frozen=True)
class Monoid(metaclass=_MonoidMeta):
    """Monoid typeclass

    Minimal complete definition:

    - ``empty`` (as a class method via metaclass)

    - ``append``

    """


    def append(self, x):
        """m -> m -> m"""
        raise NotImplementedError()
