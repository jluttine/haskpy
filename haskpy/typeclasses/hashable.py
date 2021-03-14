"""Hashability for types

.. autosummary::
   :toctree:

   Hashable

"""

from hypothesis import given, strategies as st

from haskpy.typeclasses.equality import Eq
from haskpy.internal import (
    abstract_class_function,
    abstract_function,
    class_function,
)
from haskpy import testing


class Hashable(Eq):
    """Hashable typeclass

    Minimal complete definition::

        __hash__

    Similary as in PureScript, ``Hashable`` is a subclass of ``Eq``.

    """

    @abstract_function
    def __hash__(self):
        pass

    @class_function
    def sample_hashable_type(cls):
        """Sample a hashable type

        By default, :py:meth:`.Eq.sample_eq_type` is used. If Hashable type
        requires more constraints than Eq type, override this default
        implementation.

        """
        return cls.sample_eq_type()

    @class_function
    def assert_hashable_equality(cls, x, y):
        assert hash(x) == hash(y) if x == y else True
        return

    @class_function
    @given(st.data())
    def test_hashable_equality(cls, data):
        """Test that hash is equal for equal values"""

        a = data.draw(testing.sample_hashable_type())

        x = data.draw(a)
        y = data.draw(a)

        cls.assert_hashable_equality(x, y)
        return
