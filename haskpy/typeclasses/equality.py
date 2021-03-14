"""Equality and inequality for types

.. autosummary::
   :toctree:

   Eq
   eq
   ne

"""

import hypothesis.strategies as st
from hypothesis import given

from .typeclass import Type
from haskpy.internal import class_function
from haskpy import testing
from haskpy.types.function import function


class Eq(Type):
    """Equality and inequality comparison

    Minimal complete definition:

    ..

        (__eq__ | __ne__) & sample_type

    Minimal complete definition for type constructors:

    ..

        (__eq_generic__ | (__eq_test__ & (__eq__ | __ne__))) & sample_eq_type

    """

    def __eq__(self, other):
        """Equality comparison: ``Eq a => a -> a -> bool``

        Can be used as ``==`` operator.

        The default implementation uses ``__ne__``.

        """
        return not self.__ne__(other)

    def __ne__(self, other):
        """Inequality comparison: ``Eq a => a -> a -> bool``

        Can be used as ``!=`` operator.

        The default implementation uses ``__eq__``.

        """
        return not self.__eq__(other)

    #
    # Sampling functions for property tests
    #

    @class_function
    def sample_eq_type(cls):
        """Sample Eq type

        By default, assume that the type is always Eq. Subclasses should
        override this when needed, for instance, if a type from a type
        constructor is Eq only if it's type argument is Eq (e.g., Maybe)

        """
        return cls.sample_type()

    #
    # Test typeclass laws
    #

    @class_function
    def assert_eq_reflexivity(cls, x):
        assert (x == x) is True
        return

    @class_function
    @given(st.data())
    def test_eq_reflexivity(cls, data):
        """Test ``x == x = True``"""
        a = data.draw(cls.sample_eq_type())
        x = data.draw(a)
        cls.assert_eq_reflexivity(x)
        return

    @class_function
    def assert_eq_symmetry(cls, x, y):
        assert (x == y) == (y == x)
        return

    @class_function
    @given(st.data())
    def test_eq_symmetry(cls, data):
        """Test ``x == y = y == x``"""
        a = data.draw(cls.sample_eq_type())
        x = data.draw(a)
        y = data.draw(a)
        cls.assert_eq_symmetry(x, y)
        return

    @class_function
    def assert_eq_transitivity(cls, x, y, z):
        cond = (x == y) and (y == z)
        then = (x == z)
        assert (cond and then) or (not cond)
        return

    @class_function
    @given(st.data())
    def test_eq_transitivity(cls, data):
        """Test if ``x == y && y == z = True``, then ``x == z = True``"""
        a = data.draw(cls.sample_eq_type())
        x = data.draw(a)
        y = data.draw(a)
        z = data.draw(a)
        cls.assert_eq_transitivity(x, y, z)
        return

    @class_function
    def assert_eq_substitutivity(cls, x, y, f):
        cond = (x == y)
        then = (f(x) == f(y))
        assert (cond and then) or (not cond)
        return

    @class_function
    @given(st.data())
    def test_eq_substitutivity(cls, data):
        """Test if ``x == y = True``, then ``f(x) == f(y) = True``"""

        # Draw types
        a = data.draw(cls.sample_eq_type())
        b = data.draw(testing.sample_eq_type())

        # Draw values
        x = data.draw(a)
        y = data.draw(a)
        f = data.draw(testing.sample_function(b))

        # Note: the only requirement for arbitrary functions is that the input
        # variable has __eq__ implemented. And we have that for Eq type so this
        # test can always be run.
        cls.assert_eq_substitutivity(x, y, f)
        return

    @class_function
    def assert_eq_negation(cls, x, y):
        neq = (x != y)
        eq = (x == y)
        assert (neq == (not eq))
        return

    @class_function
    @given(st.data())
    def test_eq_negation(cls, data):
        """Test ``x != y = not (x == y)``"""
        a = data.draw(cls.sample_eq_type())
        x = data.draw(a)
        y = data.draw(a)
        cls.assert_eq_negation(x, y)
        return

    #
    # Test default implementations
    #

    @class_function
    def assert_eq_eq(cls, x, y):
        assert (x == y) == eq(x, y)
        assert (x == y) == cls.__eq__(x, y)
        return

    @class_function
    @given(st.data())
    def test_eq_eq(cls, data):
        a = data.draw(cls.sample_eq_type())
        x = data.draw(a)
        y = data.draw(a)
        cls.assert_eq_eq(x, y)
        return

    @class_function
    def assert_eq_ne(cls, x, y):
        from haskpy.functions import ne
        assert (x != y) == ne(x, y)
        assert (x != y) == cls.__ne__(x, y)
        return

    @class_function
    @given(st.data())
    def test_eq_ne(cls, data):
        a = data.draw(cls.sample_eq_type())
        x = data.draw(a)
        y = data.draw(a)
        cls.assert_eq_eq(x, y)
        return


@function
def eq(x, y):
    """Equality: ``Eq a => a -> a -> Bool``

    Note that one can use `==` operator instead of this function. But operators
    cannot be partially applied in Python, so for that usecase this function
    can be useful.

    .. code-block:: python

       >>> from haskpy import List, map
       >>> map(eq(42), List(1, 2, 42, 666, 42)
       List(False, False, True, False, True)

    """
    return x == y


@function
def ne(x, y):
    """Inequality: ``Eq a => a -> a -> Bool``"""
    return x != y
