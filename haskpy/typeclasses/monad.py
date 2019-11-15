import attr
import hypothesis.strategies as st
from hypothesis import given

from .applicative import Applicative
from haskpy.utils import identity, assert_output
from haskpy import testing


class _MonadMeta(type(Applicative)):

    #
    # Test typeclass laws
    #

    @assert_output
    def assert_monad_left_identity(cls, f, a):
        return (f(a), cls.pure(a).bind(f))


    @given(st.data())
    def test_monad_left_identity(cls, data):
        # Draw types
        ta = data.draw(testing.sample_hashable_type())
        tb = data.draw(testing.sample_type())

        # Draw values
        f = data.draw(testing.sample_function(cls.sample_functor_value(tb)))
        a = data.draw(ta)

        cls.assert_monad_left_identity(f, a, data=data)
        return


    @assert_output
    def assert_monad_right_identity(cls, m):
        return (m, m.bind(cls.pure))


    @given(st.data())
    def test_monad_right_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())

        # Draw values
        m = data.draw(cls.sample_functor_value(a))

        cls.assert_monad_right_identity(m, data=data)
        return


    @assert_output
    def assert_monad_associativity(cls, m, f, g):
        return (
            m.bind(f).bind(g),
            m.bind(lambda x: f(x).bind(g)),
        )


    @given(st.data())
    def test_monad_associativity(cls, data):
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_hashable_type())
        c = data.draw(testing.sample_type())

        m = data.draw(cls.sample_functor_value(a))
        f = data.draw(testing.sample_function(cls.sample_functor_value(b)))
        g = data.draw(testing.sample_function(cls.sample_functor_value(c)))

        cls.assert_monad_associativity(m, f, g, data=data)
        return


    #
    # Test laws based on default implementations
    #


    @assert_output
    def assert_monad_bind(cls, u, f):
        from haskpy.functions import bind
        return (
            Monad.bind(u, f),
            u.bind(f),
            bind(u, f),
        )


    @given(st.data())
    def test_monad_bind(cls, data):
        """Test consistency of ``bind`` with the default implementation"""
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        u = data.draw(cls.sample_functor_value(a))
        f = data.draw(testing.sample_function(cls.sample_functor_value(b)))

        cls.assert_monad_bind(u, f, data=data)
        return


    @assert_output
    def assert_monad_join(cls, u):
        from haskpy.functions import join
        return (
            Monad.join(u),
            u.join(),
            join(u),
        )


    @given(st.data())
    def test_monad_join(cls, data):
        """Test consistency of ``join`` with the default implementation"""
        # Draw types
        b = data.draw(testing.sample_type())

        # Draw values
        u = data.draw(cls.sample_functor_value(cls.sample_functor_value(b)))

        cls.assert_monad_join(u, data=data)
        return


    @assert_output
    def assert_monad_map(cls, u, f):
        return (
            Monad.map(u, f),
            u.map(f),
        )


    @given(st.data())
    def test_monad_map(cls, data):
        """Test consistency of ``map`` with the default implementation"""
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        u = data.draw(cls.sample_functor_value(a))
        f = data.draw(testing.sample_function(b))

        cls.assert_monad_map(u, f, data=data)
        return


    @assert_output
    def assert_monad_apply(cls, u, v):
        return (
            Monad.apply(v, u),
            v.apply(u),
        )


    @given(st.data())
    def test_monad_apply(cls, data):
        """Test consistency ``apply`` with the default implementations"""
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))
        u = data.draw(cls.sample_functor_value(testing.sample_function(b)))

        cls.assert_monad_apply(u, v, data=data)
        return



class Monad(Applicative, metaclass=_MonadMeta):
    """Monad typeclass

    Minimum required implementations:

    - pure
    - one of the following:
      - bind
      - join and map

    The required Applicative methods are given default implementations based on
    the required Monad methods. But it is recommended to implement other
    methods as well if speed has any relevance.

    """


    def bind(self, f):
        """m a -> (a -> m b) -> m b

        Default implementation is based on ``join`` and ``map``:

        self :: m a

        f :: a -> m b

        map f :: m a -> m (m b)

        join :: m (m b) -> m b
        """
        return self.map(f).join()


    def join(self):
        """m (m a) -> m a

        Default implementation is based on ``bind``:

        self :: m (m a)

        identity :: m a -> m a

        bind :: m (m a) -> (m a -> m a) -> m a

        """
        return self.bind(identity)


    def apply(self, f):
        r"""m a -> m (a -> b) -> m b

          self :: m a

          f :: m (a -> b)

        Default implementation is based on ``bind`` and ``map``. In order to
        use ``bind``, let's write its type as follows:

          bind :: m (a -> b) -> ((a -> b) -> m b) -> m b

        Let's also use a simple helper function:

          h = \g -> map g self :: (a -> b) -> m b

        Now:

          bind f h :: m b

        """
        return f.bind(lambda g: self.map(g))


    def map(self, f):
        """m a -> (a -> b) -> m b

        Default implementation is based on ``bind`` and ``pure``. This
        implementation needs to be provided because the default implementation
        of ``apply`` uses ``map`` thus creating a circular dependency between
        the default ``map`` defined in ``Applicative``.

        """
        # Because of circular dependencies, need to import here inside
        from haskpy.functions import compose
        cls = type(self)
        return self.bind(compose(cls.pure, f))


# Monad-related functions are defined in function module because of circular
# dependency.
