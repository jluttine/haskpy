import attr
from hypothesis import given
import hypothesis.strategies as st

from haskpy.utils import identity
from .functor import Functor


class _ApplicativeMeta(type(Functor)):


    def pure(cls, x):
        """a -> m a"""
        raise NotImplementedError()


    def assert_applicative_identity(cls, v, eqmap=identity):
        cls.assert_equal(
            eqmap,
            cls.pure(identity).apply_to(v),
            v
        )
        return


    @given(st.data())
    def test_applicative_identity(cls, data):
        t = cls.assert_applicative_identity
        t(data.draw(cls.sample(st.integers())))
        t(data.draw(cls.sample(st.dates())))
        t(data.draw(cls.sample(cls.sample(st.integers()))))
        return


    def assert_applicative_composition(cls, u, v, w, eqmap=identity):
        from haskpy.functions import compose
        cls.assert_equal(
            eqmap,
            cls.pure(compose).apply_to(u).apply_to(v).apply_to(w),
            u.apply_to(v.apply_to(w))
        )
        return


    @given(st.data())
    def test_applicative_composition(cls, data):
        t = cls.assert_applicative_composition
        draw = lambda e: data.draw(cls.sample(e))
        t(
            # Create some random functions
            draw(st.integers().map(lambda i: lambda x: x * i)),
            draw(st.integers().map(lambda i: lambda x: x + i)),
            draw(st.integers()),
        )
        from haskpy.functions import map
        # Nested structure
        t(
            draw(st.integers().map(lambda i: map(lambda x: x * i))),
            draw(st.integers().map(lambda i: map(lambda x: x + i))),
            draw(cls.sample(st.integers())),
        )
        return


    def assert_applicative_homomorphism(cls, f, x, eqmap=identity):
        cls.assert_equal(
            eqmap,
            cls.pure(f).apply_to(cls.pure(x)),
            cls.pure(f(x))
        )
        return


    @given(st.data())
    def test_applicative_homomorphism(cls, data):
        cls.assert_applicative_homomorphism(
            # Create randomish functions
            data.draw(st.integers().map(lambda i: lambda x: x * i)),
            data.draw(st.integers())
        )
        return


    def assert_applicative_interchange(cls, u, y, eqmap=identity):
        cls.assert_equal(
            eqmap,
            u.apply_to(cls.pure(y)),
            cls.pure(lambda f: f(y)).apply_to(u)
        )
        return


    @given(st.data())
    def test_applicative_interchange(cls, data):
        cls.assert_applicative_interchange(
            data.draw(cls.sample(st.integers().map(lambda i: lambda x: x * i))),
            data.draw(st.integers())
        )
        return


    def assert_applicative_apply(cls, u, v, eqmap=identity):
        from haskpy.functions import apply
        cls.assert_equal(eqmap, apply(u, v), v.apply(u))
        cls.assert_equal(eqmap, v.apply(u), u.apply_to(v))
        return


    @given(st.data())
    def test_applicative_apply(cls, data):
        cls.assert_applicative_apply(
            data.draw(cls.sample(st.integers().map(lambda i: lambda x: x * i))),
            data.draw(cls.sample(st.integers()))
        )
        return


@attr.s(frozen=True)
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


# Applicative-related functions are defined in function module because of
# circular dependency.
