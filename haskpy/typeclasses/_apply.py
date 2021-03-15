from hypothesis import given
import hypothesis.strategies as st

from haskpy.testing import assert_output
from haskpy import testing
from haskpy.internal import class_function

# Use the "hidden" module in order to avoid circular imports
from ._functor import Functor


class Apply(Functor):
    """Apply typeclass

    :py:class:`.Apply` is to :py:class:`.Applicative` as :py:class:`.Semigroup`
    is to :py:class:`.Monoid`.

    Minimal complete definition::

        map | (apply | apply_to)

    Why do we need :py:class:`.Apply` in addition to :py:class:`.Applicative`?
    For instance, :py:class:`.Dictionary` is an instance of :py:class:`.Apply`
    but not :py:class:`.Applicative`.

    References
    ----------

    - `Apply at PureScript Pursuit
      <https://pursuit.purescript.org/packages/purescript-prelude/3.0.0/docs/Control.Apply>`_

    """

    def apply(self, f):
        """m a -> m (a -> b) -> m b

        Default implementation is based on ``apply_to``.

        """
        return f.apply_to(self)

    def apply_to(self, x):
        """f (a -> b) -> f a -> f b

        Default implementation is based on ``apply``.

        """
        return x.apply(self)

    def apply_first(self, x):
        """Combine two actions, keeping only the result of the first

        ::

            Apply f => f a -> f b -> f a

        """
        from haskpy.utils import const
        return self.map(const).apply_to(x)

    def apply_second(self, x):
        """Combine two actions, keeping only the result of the second

        ::

            Apply f => f a -> f b -> f b

        """
        from haskpy.utils import identity
        return self.replace(identity).apply_to(x)

    def __matmul__(self, x):
        """Application operand ``@`` applies similarly as ``<*>`` in Haskell

        ``f @ x`` translates to ``f.apply_to(x)``, ``x.apply(f)`` and
        ``apply(f, x)``.

        Why ``@`` operator?

        - It's not typically used as often as some other more common operators
          so less risk for confusion.

        - The operator is not a commutative as isn't ``apply`` either.

        - If we see matrix as some structure, then matrix multiplication takes
          both left and right operand inside this structure and gives a result
          also inside this structure, similarly as ``apply`` does. So it's an
          operator for two operands having a similar structure.

        - The operator evaluates the contained function(s) at the contained
          value(s). Thus, ``f`` "at" ``x`` makes perfect sense.

        """
        return self.apply_to(x)

    def __lshift__(self, x):
        """Sequence with ``<<`` similarly as with ``<*`` and ``<<`` in Haskell"""
        return self.apply_first(x)

    def __rshift__(self, x):
        """Sequence with ``>>`` similarly as with ``*>`` and ``>>`` in Haskell"""
        return self.apply_second(x)

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_apply_type_constructor(cls):
        """Sample an apply type constructor

        By default, :py:meth:`.Functor.sample_functor_type_constructor` is
        used. If Apply type requires more constraints than Functor type,
        override this default implementation.

        """
        return cls.sample_functor_type_constructor()

    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_apply_associative_composition(cls, u, v, w):
        """u @ (v @ w) == ((compose ** u) @ v) @ w"""
        from haskpy.types.function import compose
        return (
            u.apply_to(v.apply_to(w)),
            u.map(compose).apply_to(v).apply_to(w),
        )

    @class_function
    @given(st.data())
    def test_apply_associative_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_type())
        f = data.draw(cls.sample_apply_type_constructor())
        fa = f(a)
        fab = f(testing.sample_function(b))
        fbc = f(testing.sample_function(c))

        # Draw values
        w = data.draw(fa)
        v = data.draw(fab)
        u = data.draw(fbc)

        cls.assert_apply_associative_composition(u, v, w, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_apply_apply(cls, u, v):
        from .apply_ import apply
        return (
            v.apply(u),
            apply(u, v),
            u.apply_to(v),
            u @ v,
        )

    @class_function
    @given(st.data())
    def test_apply_apply(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_apply_type_constructor())
        fa = f(a)
        fab = f(testing.sample_function(b))

        # Draw values
        v = data.draw(fa)
        u = data.draw(fab)

        cls.assert_apply_apply(u, v, data=data)
        return

    @class_function
    @assert_output
    def assert_apply_apply_first(cls, u, v):
        from .apply_ import apply_first
        return (
            Apply.apply_first(u, v),
            u.apply_first(v),
            apply_first(u, v),
            u << v,
        )

    @class_function
    @given(st.data())
    def test_apply_apply_first(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_apply_type_constructor())
        fa = f(a)
        fb = f(b)

        # Draw values
        u = data.draw(fa)
        v = data.draw(fb)

        cls.assert_apply_apply_first(u, v, data=data)
        return

    @class_function
    @assert_output
    def assert_apply_apply_second(cls, u, v):
        from .apply_ import apply_second
        return (
            Apply.apply_second(u, v),
            u.apply_second(v),
            apply_second(u, v),
            u >> v,
        )

    @class_function
    @given(st.data())
    def test_apply_apply_second(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_apply_type_constructor())
        fa = f(a)
        fb = f(b)

        # Draw values
        u = data.draw(fa)
        v = data.draw(fb)

        cls.assert_apply_apply_second(u, v, data=data)
        return
