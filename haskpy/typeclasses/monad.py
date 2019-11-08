import attr
import hypothesis.strategies as st
from hypothesis import given

from .applicative import Applicative
from haskpy.utils import identity, assert_output
from haskpy import testing


class _MonadMeta(type(Applicative)):


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

        cls.assert_monad_left_identity(f, a)
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

        cls.assert_monad_right_identity(m)
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

        cls.assert_monad_associativity(m, f, g)
        return


@attr.s(frozen=True)
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
        use ``bind``, we need to have a function of type:

          g :: a -> m b

        We can get this as follows:

          g = \x -> map (\fh -> fh x) f

        """
        return self.bind(lambda x: f.map(lambda fh: fh(x)))


    def map(self, f):
        """m a -> (a -> b) -> m b

        Default implementation is based on ``bind`` and ``pure``. This
        implementation needs to be provided because the default implementation
        of ``apply`` uses ``map``.

        """
        # Because of circular depdencies, need to import here inside
        from haskpy.functions import compose
        cls = type(self)
        return self.bind(compose(cls.pure, f))


# Monad-related functions are defined in function module because of circular
# dependency.
