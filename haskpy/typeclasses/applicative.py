import attr
from hypothesis import given
import hypothesis.strategies as st

from haskpy.utils import identity, assert_output
from .functor import Functor
from haskpy import testing


class _ApplicativeMeta(type(Functor)):


    def pure(cls, x):
        """a -> m a"""
        raise NotImplementedError()


    #
    # Test typeclass laws
    #

    @assert_output
    def assert_applicative_identity(cls, v):
        return (
            v,
            cls.pure(identity).apply_to(v),
        )


    @given(st.data())
    def test_applicative_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))

        cls.assert_applicative_identity(v, data=data)
        return


    @assert_output
    def assert_applicative_composition(cls, u, v, w):
        from haskpy.functions import compose
        return (
            u.apply_to(v.apply_to(w)),
            cls.pure(compose).apply_to(u).apply_to(v).apply_to(w),
        )


    @given(st.data())
    def test_applicative_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_hashable_type())
        c = data.draw(testing.sample_type())

        # Draw values
        w = data.draw(cls.sample_functor_value(a))
        v = data.draw(cls.sample_functor_value(testing.sample_function(b)))
        u = data.draw(cls.sample_functor_value(testing.sample_function(c)))

        cls.assert_applicative_composition(u, v, w, data=data)
        return


    @assert_output
    def assert_applicative_homomorphism(cls, f, x):
        return (
            cls.pure(f).apply_to(cls.pure(x)),
            cls.pure(f(x))
        )


    @given(st.data())
    def test_applicative_homomorphism(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(a)
        f = data.draw(testing.sample_function(b))

        cls.assert_applicative_homomorphism(f, x, data=data)
        return


    @assert_output
    def assert_applicative_interchange(cls, u, y):
        return (
            u.apply_to(cls.pure(y)),
            cls.pure(lambda f: f(y)).apply_to(u)
        )


    @given(st.data())
    def test_applicative_interchange(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        y = data.draw(a)
        u = data.draw(cls.sample_functor_value(testing.sample_function(b)))

        cls.assert_applicative_interchange(u, y, data=data)
        return


    #
    # Test laws based on default implementations
    #


    @assert_output
    def assert_applicative_apply(cls, u, v):
        from haskpy.functions import apply
        return (
            v.apply(u),
            apply(u, v),
            u.apply_to(v),
        )


    @given(st.data())
    def test_applicative_apply(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))
        u = data.draw(cls.sample_functor_value(testing.sample_function(b)))

        cls.assert_applicative_apply(u, v, data=data)
        return


    @assert_output
    def assert_applicative_sequence(cls, u, v):
        from haskpy.functions import sequence
        return (
            Applicative.sequence(u, v),
            u.sequence(v),
            sequence(u, v),
        )


    @given(st.data())
    def test_applicative_sequence(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        b = data.draw(testing.sample_type())

        # Draw values
        u = data.draw(cls.sample_functor_value(a))
        v = data.draw(cls.sample_functor_value(b))

        cls.assert_applicative_sequence(u, v, data=data)
        return


    @assert_output
    def assert_applicative_map(cls, v, f):
        return(
            Applicative.map(v, f),
            v.map(f),
        )


    @given(st.data())
    def test_applicative_map(cls, data):
        """Test consistency between Applicative and Functor implementations"""
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))
        f = data.draw(testing.sample_function(b))

        cls.assert_applicative_map(v, f, data=data)
        return


class Applicative(Functor, metaclass=_ApplicativeMeta):
    """Must define at least pure and either apply or apply_to

    The required Functor methods are given defaults based on the required
    Applicative methods.

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
        """Use ``@`` as apply operator similarly as ``<*>`` in Haskell

        ``f @ x`` translates to ``f.apply_to(x)`` or ``x.apply(f)``.

        """
        return self.apply_to(x)


    def __rshift__(self, x):
        """Sequence with``>>`` similarly as with ``*>`` and ``>>`` in Haskell"""
        return self.sequence(x)



# Applicative-related functions are defined in function module because of
# circular dependency.
