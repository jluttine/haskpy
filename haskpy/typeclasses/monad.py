import hypothesis.strategies as st
from hypothesis import given

from .applicative import Applicative
from haskpy.utils import (
    identity,
    assert_output,
    class_function,
    abstract_class_function,
)
from haskpy import testing


class Monad(Applicative):
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

    def __mod__(self, f):
        """Use ``%`` as bind operator similarly as ``>>=`` in Haskell

        That is, ``x % f`` is equivalent to ``bind(x, f)`` and ``x.bind(f)``.

        Why ``%`` operator?

        - It's not very often used so less risk for confusion.

        - It's not commutative as isn't bind either.

        - It is similar to bind in a sense that the result has the same unit as
          the left operand while the right operand has different unit.

        - The symbol works visually as a line "binds" two circles and on the
          other hand two circles tell about two similar structures on both
          sides but those structures are just on different "level".

        """
        return self.bind(f)

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_monad_type(cls, a):
        pass

    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_monad_left_identity(cls, f, a):
        return (f(a), cls.pure(a).bind(f))

    @class_function
    @given(st.data())
    def test_monad_left_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        mb = data.draw(cls.sample_monad_type(b))

        # Draw values
        f = data.draw(testing.sample_function(mb))
        x = data.draw(a)

        cls.assert_monad_left_identity(f, x, data=data)
        return

    @class_function
    @assert_output
    def assert_monad_right_identity(cls, m):
        return (m, m.bind(cls.pure))

    @class_function
    @given(st.data())
    def test_monad_right_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        ma = data.draw(cls.sample_monad_type(a))

        # Draw values
        m = data.draw(ma)

        cls.assert_monad_right_identity(m, data=data)
        return

    @class_function
    @assert_output
    def assert_monad_associativity(cls, m, f, g):
        return (
            m.bind(f).bind(g),
            m.bind(lambda x: f(x).bind(g)),
        )

    @class_function
    @given(st.data())
    def test_monad_associativity(cls, data):
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_type())
        ma = data.draw(cls.sample_monad_type(a))
        mb = data.draw(cls.sample_monad_type(b))
        mc = data.draw(cls.sample_monad_type(c))

        m = data.draw(ma)
        f = data.draw(testing.sample_function(mb))
        g = data.draw(testing.sample_function(mc))

        cls.assert_monad_associativity(m, f, g, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_monad_bind(cls, u, f):
        from haskpy.functions import bind
        return (
            Monad.bind(u, f),
            u.bind(f),
            bind(u, f),
        )

    @class_function
    @given(st.data())
    def test_monad_bind(cls, data):
        """Test consistency of ``bind`` with the default implementation"""
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        ma = data.draw(cls.sample_monad_type(a))
        mb = data.draw(cls.sample_monad_type(b))

        # Draw values
        u = data.draw(ma)
        f = data.draw(testing.sample_function(mb))

        cls.assert_monad_bind(u, f, data=data)
        return

    @class_function
    @assert_output
    def assert_monad_join(cls, u):
        from haskpy.functions import join
        return (
            Monad.join(u),
            u.join(),
            join(u),
        )

    @class_function
    @given(st.data())
    def test_monad_join(cls, data):
        """Test consistency of ``join`` with the default implementation"""
        # Draw types
        b = data.draw(testing.sample_type())
        mb = data.draw(cls.sample_monad_type(b))
        mmb = data.draw(cls.sample_monad_type(mb))

        # Draw values
        u = data.draw(mmb)

        cls.assert_monad_join(u, data=data)
        return

    @class_function
    @assert_output
    def assert_monad_map(cls, u, f):
        return (
            Monad.map(u, f),
            u.map(f),
        )

    @class_function
    @given(st.data())
    def test_monad_map(cls, data):
        """Test consistency of ``map`` with the default implementation"""
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        ma = data.draw(cls.sample_monad_type(a))

        u = data.draw(ma)
        f = data.draw(testing.sample_function(b))

        cls.assert_monad_map(u, f, data=data)
        return

    @class_function
    @assert_output
    def assert_monad_apply(cls, u, v):
        return (
            Monad.apply(v, u),
            v.apply(u),
        )

    @class_function
    @given(st.data())
    def test_monad_apply(cls, data):
        """Test consistency ``apply`` with the default implementations"""
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        ma = data.draw(cls.sample_monad_type(a))
        mab = data.draw(cls.sample_monad_type(testing.sample_function(b)))

        # Draw values
        v = data.draw(ma)
        u = data.draw(mab)

        cls.assert_monad_apply(u, v, data=data)
        return


# Monad-related functions are defined in function module because of circular
# dependency.
