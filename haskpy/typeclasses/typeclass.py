import hypothesis.strategies as st
import attr


class _TypeMeta(type):
    """Base metaclass for typeclasses"""


    def __repr__(cls):
        return cls.__name__


    def sample(cls, *_, **__):
        raise NotImplementedError()


class Type(metaclass=_TypeMeta):


    def __eq__(self, other):
        raise TypeError("Eq not supported by default.")


    def __test_eq__(self, x, data=None):
        """Equality used in unit tests

        For some types, such as functions, direct == doesn't work but one needs
        to compare the function outputs for many input points. Then, data can
        be useful. But for most cases, normal equality works just fine.

        """
        return self == x
