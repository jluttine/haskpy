from .typeclass import Type
from haskpy.utils import class_function


class Eq(Type):
    """Equality and inequality comparison

    Minimal complete definition:

    - ``__eq__`` or ``__neq__``

    """

    def __eq__(self, other):
        """Equality comparison: ``Eq a => a -> a -> bool``

        Can be used as ``==`` operator.

        The default implementation uses ``__neq__``.

        """
        return not self.__neq__(other)

    def __neq__(self, other):
        """Inequality comparison: ``Eq a => a -> a -> bool``

        Can be used as ``!=`` operator.

        The default implementation uses ``__eq__``.

        """
        return not self.__eq__(other)

    @class_function
    def sample_eq_type(cls):
        # By default, assume that the type is always Eq. Subclasses should
        # override this when needed, for instance, if a type from a type
        # constructor is Eq only if it's type argument is Eq (e.g., Maybe)
        return cls.sample_type()


# TODO: ADD EQ LAW TESTS!!!
