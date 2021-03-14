from hypothesis import given
import hypothesis.strategies as st

from haskpy.testing import assert_output
from haskpy import testing
from haskpy.internal import (
    class_function,
    abstract_class_function,
)

# Use the "hidden" module in order to avoid circular imports
from ._apply import Apply


class Applicative(Apply):
    """Applicative functor typeclass.

    Minimal complete definition::

        pure | (apply | apply_to)

    The required Functor methods are given defaults based on the required
    Applicative methods, so you don't need to implement ``map`` method.

    References
    ----------

    - C. McBride and R. Paterson, "Applicative programming with effects",
      Journal of Functional Programming , Volume 18 , Issue 1 , January 2008 ,
      pp. 1 - 13. DOI: `<https://doi.org/10.1017/S0956796807006326>`_

    - `Applicative functor at Haskell Wiki
      <https://wiki.haskell.org/Applicative_functor>`_.

    - `Applicative at Hackage
      <https://hackage.haskell.org/package/base/docs/Control-Applicative.html>`_

    """

    @abstract_class_function
    def pure(cls, x):
        """a -> m a"""

    def map(self, f):
        """m a -> (a -> b) -> m b

        Default implementation is based on ``apply``:

        self :: m a

        f :: a -> b

        pure f :: m (a -> b)

        apply :: m a -> m (a -> b) -> m b

        """
        # Default implementation for Functor based on Applicative
        cls = type(self)
        mf = cls.pure(f)
        return self.apply(mf)

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_applicative_type_constructor(cls):
        """Sample an applicative type

        By default, :py:meth:`.Apply.sample_apply_type_constructor` is used. If
        Applicative type requires more constraints than Apply type, override
        this default implementation.

        """
        return cls.sample_apply_type_constructor()

    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_applicative_identity(cls, v):
        from haskpy.utils import identity
        return (
            v,
            cls.pure(identity).apply_to(v),
        )

    @class_function
    @given(st.data())
    def test_applicative_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        f = data.draw(cls.sample_applicative_type_constructor())
        fa = f(a)

        # Draw values
        v = data.draw(fa)

        cls.assert_applicative_identity(v, data=data)
        return

    @class_function
    @assert_output
    def assert_applicative_composition(cls, u, v, w):
        from haskpy.types.function import compose
        return (
            u.apply_to(v.apply_to(w)),
            cls.pure(compose).apply_to(u).apply_to(v).apply_to(w),
        )

    @class_function
    @given(st.data())
    def test_applicative_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_type())
        f = data.draw(cls.sample_applicative_type_constructor())
        fa = f(a)
        fab = f(testing.sample_function(b))
        fbc = f(testing.sample_function(c))

        # Draw values
        w = data.draw(fa)
        v = data.draw(fab)
        u = data.draw(fbc)

        cls.assert_applicative_composition(u, v, w, data=data)
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
        f = data.draw(cls.sample_applicative_type_constructor())
        fab = f(testing.sample_function(b))

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
    def assert_applicative_map(cls, v, f):
        return(
            Applicative.map(v, f),
            v.map(f),
        )

    @class_function
    @given(st.data())
    def test_applicative_map(cls, data):
        """Test consistency between Applicative and Functor implementations"""
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_applicative_type_constructor())
        fa = f(a)

        # Draw values
        v = data.draw(fa)
        f = data.draw(testing.sample_function(b))

        cls.assert_applicative_map(v, f, data=data)
        return
