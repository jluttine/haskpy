import hypothesis.strategies as st
from hypothesis import given

from haskpy.internal import class_function
from haskpy.testing import assert_output
from haskpy import testing

# Use the "hidden" module in order to avoid circular imports
from ._apply import Apply


class Bind(Apply):
    """Bind typeclass extends :py:class:`.Apply` with a bind operation

    Minimal complete definition::

        map & (bind | join)

    Typeclass laws:

    - Associativity: ``(x % f) % g = x % (lambda k: f(k) % g)``

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
        from haskpy.utils import identity
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

    @class_function
    def sample_bind_type_constructor(cls):
        """Sample type constructor of Bind instance

        By default, :py:meth:`.Apply.sample_apply_type_constructor` is used. If
        Bind type requires more constraints than pply type, override this
        default implementation.

        """
        return cls.sample_apply_type_constructor()

    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_bind_associativity(cls, m, f, g):
        return (
            m.bind(f).bind(g),
            m.bind(lambda x: f(x).bind(g)),
        )

    @class_function
    @given(st.data())
    def test_bind_associativity(cls, data):
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_type())
        m = data.draw(cls.sample_bind_type_constructor())
        ma = m(a)
        mb = m(b)
        mc = m(c)

        m = data.draw(ma)
        f = data.draw(testing.sample_function(mb))
        g = data.draw(testing.sample_function(mc))

        cls.assert_bind_associativity(m, f, g, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_bind_bind(cls, u, f):
        from .bind_ import bind
        return (
            Bind.bind(u, f),
            u.bind(f),
            bind(u, f),
        )

    @class_function
    @given(st.data())
    def test_bind_bind(cls, data):
        """Test consistency of ``bind`` with the default implementation"""
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        m = data.draw(cls.sample_bind_type_constructor())
        ma = m(a)
        mb = m(b)

        # Draw values
        u = data.draw(ma)
        f = data.draw(testing.sample_function(mb))

        cls.assert_bind_bind(u, f, data=data)
        return

    @class_function
    @assert_output
    def assert_bind_join(cls, u):
        from .bind_ import join
        return (
            Bind.join(u),
            u.join(),
            join(u),
        )

    @class_function
    @given(st.data())
    def test_bind_join(cls, data):
        """Test consistency of ``join`` with the default implementation"""
        # Draw types
        b = data.draw(testing.sample_type())
        m = data.draw(cls.sample_bind_type_constructor())
        mb = m(b)
        mmb = m(mb)

        # Draw values
        u = data.draw(mmb)

        cls.assert_bind_join(u, data=data)
        return

    @class_function
    @assert_output
    def assert_bind_apply(cls, u, v):
        return (
            Bind.apply(v, u),
            v.apply(u),
        )

    @class_function
    @given(st.data())
    def test_bind_apply(cls, data):
        """Test consistency ``apply`` with the default implementations"""
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        m = data.draw(cls.sample_bind_type_constructor())
        ma = m(a)
        mab = m(testing.sample_function(b))

        # Draw values
        v = data.draw(ma)
        u = data.draw(mab)

        cls.assert_bind_apply(u, v, data=data)
        return
