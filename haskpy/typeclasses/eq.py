from .typeclass import Type


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
