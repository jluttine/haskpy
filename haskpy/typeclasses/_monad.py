import hypothesis.strategies as st
from hypothesis import given

from haskpy.internal import class_function
from haskpy.testing import assert_output
from haskpy import testing

# Use the "hidden" module in order to avoid circular imports
from ._applicative import Applicative
from ._bind import Bind


class Monad(Applicative, Bind):
    """Monad typeclass

    Minimal complete definition::

        pure & (bind | (join & map))

    Typeclass laws:

    - Left identity: ``pure(x) % f = f(x)``
    - Right identity: ``x % pure = x``

    """

    def map(self, f):
        """m a -> (a -> b) -> m b

        Default implementation is based on ``bind`` and ``pure``. This
        implementation needs to be provided because the default implementation
        of ``apply`` uses ``map`` thus creating a circular dependency between
        the default ``map`` defined in ``Applicative``.

        """
        # Because of circular dependencies, need to import here inside
        from haskpy.types.function import compose
        cls = type(self)
        return self.bind(compose(cls.pure, f))

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_monad_type_constructor(cls):
        """Sample a monad type constructor

        By default, :py:meth:`.Applicative.sample_applicative_type_constructor`
        is used. If Monad type requires more constraints than Applicative type,
        override this default implementation.

        """
        return cls.sample_applicative_type_constructor()

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
        m = data.draw(cls.sample_monad_type_constructor())
        mb = m(b)

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
        m = data.draw(cls.sample_monad_type_constructor())
        ma = m(a)

        # Draw values
        m = data.draw(ma)

        cls.assert_monad_right_identity(m, data=data)
        return

    #
    # Test laws based on default implementations
    #

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
        m = data.draw(cls.sample_monad_type_constructor())
        ma = m(a)

        u = data.draw(ma)
        f = data.draw(testing.sample_function(b))

        cls.assert_monad_map(u, f, data=data)
        return
