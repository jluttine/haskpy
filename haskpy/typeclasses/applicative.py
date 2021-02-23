from hypothesis import given
import hypothesis.strategies as st

from haskpy.utils import identity, assert_output
from .functor import Functor
from haskpy import testing
from haskpy.utils import (
    class_function,
    abstract_class_function,
)


class Applicative(Functor):
    """Must define at least pure and either apply or apply_to

    The required Functor methods are given defaults based on the required
    Applicative methods.

    """

    @abstract_class_function
    def pure(cls, x):
        """a -> m a"""

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

    def sequence(self, x):
        """f a -> f b -> f b"""
        from haskpy.utils import identity
        return self.replace(identity).apply_to(x)

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

    def __rshift__(self, x):
        """Sequence with``>>`` similarly as with ``*>`` and ``>>`` in Haskell"""
        return self.sequence(x)

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_applicative_type(cls, a):
        """Sample an applicative type

        Note that it would be tempting to define:

        .. code-block:: python

            def sample_functor_type(cls, a):
                return cls.sample_applicative_type(a)

        But we can have classes that are applicatives only if some of their
        arguments are applicative too. For instance, MaybeT(cls, x) is
        functor/applicative/monad only if cls is. So, we need to have a
        separate sample_functor_type method.

        But then, how do we make sure that the sampled applicative type is also
        a functor? For instance, a pathological case could be such that
        sample_functor_ype returns something completely different type than
        sample_applicative_type. I suppose we just have to leave that as a
        responsibility for the user that sample methods are implemented
        correctly/consistently.

        """
        pass


    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_applicative_identity(cls, v):
        return (
            v,
            cls.pure(identity).apply_to(v),
        )

    @class_function
    @given(st.data())
    def test_applicative_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_applicative_type(a))

        # Draw values
        v = data.draw(fa)

        cls.assert_applicative_identity(v, data=data)
        return

    @class_function
    @assert_output
    def assert_applicative_composition(cls, u, v, w):
        from haskpy.functions import compose
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
        fa = data.draw(cls.sample_applicative_type(a))
        fab = data.draw(cls.sample_applicative_type(testing.sample_function(b)))
        fbc = data.draw(cls.sample_applicative_type(testing.sample_function(c)))

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
        fab = data.draw(cls.sample_applicative_type(testing.sample_function(b)))

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
        from haskpy.functions import apply
        return (
            v.apply(u),
            apply(u, v),
            u.apply_to(v),
        )

    @class_function
    @given(st.data())
    def test_applicative_apply(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_applicative_type(a))
        fab = data.draw(cls.sample_applicative_type(testing.sample_function(b)))

        # Draw values
        v = data.draw(fa)
        u = data.draw(fab)

        cls.assert_applicative_apply(u, v, data=data)
        return

    @class_function
    @assert_output
    def assert_applicative_sequence(cls, u, v):
        from haskpy.functions import sequence
        return (
            Applicative.sequence(u, v),
            u.sequence(v),
            sequence(u, v),
        )

    @class_function
    @given(st.data())
    def test_applicative_sequence(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        b = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_applicative_type(a))
        fb = data.draw(cls.sample_applicative_type(b))

        # Draw values
        u = data.draw(fa)
        v = data.draw(fb)

        cls.assert_applicative_sequence(u, v, data=data)
        return

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
        fa = data.draw(cls.sample_applicative_type(a))

        # Draw values
        v = data.draw(fa)
        f = data.draw(testing.sample_function(b))

        cls.assert_applicative_map(v, f, data=data)
        return


# Applicative-related functions are defined in function module because of
# circular dependency.
