from hypothesis import given
import hypothesis.strategies as st

from haskpy.testing import assert_output
from haskpy import testing
from haskpy.internal import (
    class_function,
    abstract_class_function,
)

# Use the "hidden" module in order to avoid circular imports
from ._functor import Functor


class Apply(Functor):
    """Apply typeclass

    :py:class:`.Apply` is to :py:class:`.Applicative` as :py:class:`.Semigroup`
    is to :py:class:`.Monoid`.

    Minimal complete definition::

        map | (apply | apply_to)

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
        """Sequence with``<<`` similarly as with ``<*`` and ``<<`` in Haskell"""
        return self.apply_first(x)

    def __rshift__(self, x):
        """Sequence with ``>>`` similarly as with ``*>`` and ``>>`` in Haskell"""
        return self.apply_second(x)

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_apply_type(cls, a):
        """Sample an apply type

        Note that it would be tempting to define:

        .. code-block:: python

            def sample_functor_type(cls, a):
                return cls.sample_apply_type(a)

        But we can have classes that are Apply instances only if some of their
        arguments are Apply instances too. For instance, MaybeT(cls, x) is
        functor/applicative/monad only if cls is. So, we need to have a
        separate sample_functor_type method.

        But then, how do we make sure that the sampled Apply instance type is
        also a functor? For instance, a pathological case could be such that
        sample_functor_type returns something completely different type than
        sample_apply_type. I suppose we just have to leave that as a
        responsibility for the user that sample methods are implemented
        correctly/consistently.

        """
        pass

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
        fa = data.draw(cls.sample_apply_type(a))
        fab = data.draw(cls.sample_apply_type(testing.sample_function(b)))
        fbc = data.draw(cls.sample_apply_type(testing.sample_function(c)))

        # Draw values
        w = data.draw(fa)
        v = data.draw(fab)
        u = data.draw(fbc)

        cls.assert_apply_associative_composition(u, v, w, data=data)
        return

    @class_function
    @assert_output
    def assert_applicative_homomorphism(cls, f, x):
        return (
            cls.pure(f).apply_to(cls.pure(x)),
            cls.pure(f(x))
        )

    @class_function
    @given(st.data())
    def test_applicative_homomorphism(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(a)
        f = data.draw(testing.sample_function(b))

        cls.assert_applicative_homomorphism(f, x, data=data)
        return

    @class_function
    @assert_output
    def assert_applicative_interchange(cls, u, y):
        return (
            u.apply_to(cls.pure(y)),
            cls.pure(lambda f: f(y)).apply_to(u)
        )

    @class_function
    @given(st.data())
    def test_applicative_interchange(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        fab = data.draw(cls.sample_apply_type(testing.sample_function(b)))

        # Draw values
        y = data.draw(a)
        u = data.draw(fab)

        cls.assert_applicative_interchange(u, y, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_applicative_apply(cls, u, v):
        from .apply_ import apply
        return (
            v.apply(u),
            apply(u, v),
            u.apply_to(v),
            u @ v,
        )

    @class_function
    @given(st.data())
    def test_applicative_apply(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_apply_type(a))
        fab = data.draw(cls.sample_apply_type(testing.sample_function(b)))

        # Draw values
        v = data.draw(fa)
        u = data.draw(fab)

        cls.assert_applicative_apply(u, v, data=data)
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
        fa = data.draw(cls.sample_apply_type(a))
        fb = data.draw(cls.sample_apply_type(b))

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
        fa = data.draw(cls.sample_apply_type(a))
        fb = data.draw(cls.sample_apply_type(b))

        # Draw values
        u = data.draw(fa)
        v = data.draw(fb)

        cls.assert_apply_apply_second(u, v, data=data)
        return
