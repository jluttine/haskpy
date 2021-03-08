"""Basis for typeclasses

.. autosummary::
   :toctree:

   Type

"""

from hypothesis import given
import hypothesis.strategies as st

from haskpy.internal import (
    nonexisting_function,
    abstract_class_function,
    class_function,
)


class MetaType(type):

    def __repr__(cls):
        return cls.__name__


class Type(object, metaclass=MetaType):
    """Base class for all typeclasses, type constructors and types

    Minimal complete definition for property tests:

    ..

        sample_type

    In HaskPy, typeclasses, type constructors and types are all represented by
    classes. Typeclasses are abstract base classes. Type constructors and types
    seemingly similar classes but type constructors just have some implicit
    type arguments when values are constructed.

    """

    def __dir__(self):
        xs = super().__dir__()
        return [
            x
            for x in xs
            if hasattr(self, x)
        ]

    @nonexisting_function
    def __init__(self):
        pass

    @nonexisting_function
    def __eq__(self, other):
        pass

    @nonexisting_function
    def __ne__(self, other):
        pass

    @nonexisting_function
    def __gt__(self, other):
        pass

    @nonexisting_function
    def __ge__(self, other):
        pass

    @nonexisting_function
    def __lt__(self, other):
        pass

    @nonexisting_function
    def __le__(self, other):
        pass

    @nonexisting_function
    def __str__(self):
        pass

    # IPython doesn't work properly if the type isn't hashable. See:
    # https://github.com/ipython/ipython/issues/12320
    #
    # See the workarounds in that issue or use normal Python REPL.
    @nonexisting_function
    def __hash__(self, other):
        pass

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, nonexisting_function):
            raise AttributeError()
        else:
            return attr

    #
    # Sampling functions for property tests
    #

    @abstract_class_function
    def sample_type(cls):
        """Provide a type strategy that provides a value strategy"""

    @class_function
    @given(st.data())
    def test_type(cls, data):
        """Test sampling values and that they have the correct type"""
        t = data.draw(cls.sample_type())
        x = data.draw(t)
        assert isinstance(x, cls)
        return
