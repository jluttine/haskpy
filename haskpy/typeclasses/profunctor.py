from hypothesis import given
from hypothesis import strategies as st

from .contravariant import Contravariant
from .functor import Functor
from haskpy.utils import (
    identity,
    assert_output,
    class_function,
    abstract_class_function,
)
from haskpy import testing


class Profunctor(Functor, Contravariant):
    """Profunctor

    Minimal complete definition: ``dimap | (contramap & map)``.

    Instead of using ``lmap`` and ``rmap`` as in Haskell, let's use the already
    introduced ``contramap`` and ``map``.

    """

    def dimap(self, f, g):
        """p b c -> (a -> b) -> (c -> d) -> p a d"""
        return self.contramap(f).map(g)

    def contramap(self, f):
        """(a -> b) -> p b c -> p a c"""
        return self.dimap(f, identity)

    def map(self, g):
        """(b -> c) -> p a b -> p a c"""
        return self.dimap(identity, g)

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_profunctor_type(cls, a, b):
        pass

    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_profunctor_identity(cls, x):
        return (
            x,
            x.dimap(identity, identity),
        )

    @class_function
    @given(st.data())
    def test_profunctor_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_profunctor_identity(x, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_profunctor_dimap(cls, x, f, g):
        from haskpy.functions import dimap
        return (
            Profunctor.dimap(x, f, g),
            x.dimap(f, g),
            dimap(f, g, x),
        )

    @class_function
    @given(st.data())
    def test_profunctor_dimap(cls, data):
        # Draw types
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_eq_type())
        d = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(b, c))
        f = data.draw(testing.sample_function(b))
        g = data.draw(testing.sample_function(d))

        cls.assert_profunctor_dimap(x, f, g, data=data)
        return

    @class_function
    @assert_output
    def assert_profunctor_map(cls, x, f):
        return (
            Profunctor.map(x, f),
            x.map(f),
        )

    @class_function
    @given(st.data())
    def test_profunctor_map(cls, data):
        # Draw types
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_eq_type())
        d = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(b, c))
        g = data.draw(testing.sample_function(d))

        cls.assert_profunctor_map(x, g, data=data)
        return

    @class_function
    @assert_output
    def assert_profunctor_contramap(cls, x, f):
        return (
            Profunctor.contramap(x, f),
            x.contramap(f),
        )

    @class_function
    @given(st.data())
    def test_profunctor_contramap(cls, data):
        # Draw types
        b = data.draw(testing.sample_eq_type())
        d = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(b, d))
        f = data.draw(testing.sample_function(b))

        cls.assert_profunctor_contramap(x, f, data=data)
        return


# Profunctor-related functions are defined in function module because of
# circular dependency.
