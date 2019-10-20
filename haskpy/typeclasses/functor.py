import attr

from .typeclass import TypeclassMeta


@attr.s(frozen=True)
class Functor(metaclass=TypeclassMeta):
    """Covariant functor"""


    def map(self, f):
        """Haskell fmap"""
        raise NotImplementedError()


    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)


# Functor-related functions are defined in function module because of circular
# dependency.
