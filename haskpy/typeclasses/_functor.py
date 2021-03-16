from hypothesis import given
from hypothesis import strategies as st

from .typeclass import Type
from haskpy.internal import (
    abstract_class_function,
    abstract_function,
    class_function,
)
from haskpy.testing import assert_output
from haskpy import testing


class Functor(Type):
    """Covariant functor

    Minimal complete definition:

    ..

        map

    Functor laws:

    - Identity: ``map(identity) == identity``

    - Composition: ``map(compose(f, g)) == compose(map(f), map(g))``

    For property tests:

    ..

        sample_functor_type_constructor

    Examples
    --------

    In Haskell, Map is a Functor, but not Applicative

    """

    @abstract_function
    def map(self, f):
        """Functor f => f a -> (a -> b) -> f b"""

    def flap(self, x):
        """Functor f => f (a -> b) -> a - > f b"""
        return self.map(lambda f: f(x))

    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)

    def __rpow__(self, f):
        """Lifting operator ``**`` lifts similarly as ``<$>`` in Haskell

        ``f ** x`` translates to ``x.map(f)`` and ``map(f, x)``.

        Why ``**`` operator?

        - It's not typically used as often as multiplication or addition so
          less risk of confusion.

        - It's not commutative operator as isn't lifting either.

        - The two operands have very different roles. They are not at the same
          "level".

        - The right operand is "higher", that is, it's inside a structure and
          the left operand is kind of "raised to the power" of the second
          operand, where the "power" is the functorial structure.

        - The same operand is also used for function composition because
          function composition is just mapping. Visually the symbol can be
          seen as chaining two stars similarly as function composition chains
          two functions.

        """
        return self.map(f)

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_functor_type_constructor(cls):
        pass

    #
    # Test typeclass laws
    #

    @class_function
    @assert_output
    def assert_functor_identity(cls, v):
        from haskpy.utils import identity
        return(
            v,
            v.map(identity),
        )

    @class_function
    @given(st.data())
    def test_functor_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        f = data.draw(cls.sample_functor_type_constructor())
        fa = f(a)

        # Draw values
        v = data.draw(fa)

        cls.assert_functor_identity(v, data=data)
        return

    @class_function
    @assert_output
    def assert_functor_composition(cls, v, f, g):
        return (
            v.map(f).map(g),
            v.map(lambda x: g(f(x))),
        )

    @class_function
    @given(st.data())
    def test_functor_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_type())
        f = data.draw(cls.sample_functor_type_constructor())
        fa = f(a)

        # Draw values
        v = data.draw(fa)
        g = data.draw(testing.sample_function(b))
        h = data.draw(testing.sample_function(c))

        cls.assert_functor_composition(v, g, h, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_functor_map(cls, v, f):
        from .functor import map
        return (
            v.map(f),
            map(f, v),
        )

    @class_function
    @given(st.data())
    def test_functor_map(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_functor_type_constructor())
        fa = f(a)

        # Draw values
        v = data.draw(fa)
        f = data.draw(testing.sample_function(b))

        cls.assert_functor_map(v, f, data=data)
        return

    @class_function
    @assert_output
    def assert_functor_replace(cls, v, x):
        from .functor import replace
        return (
            Functor.replace(v, x),
            replace(x, v),
            v.replace(x),
        )

    @class_function
    @given(st.data())
    def test_functor_replace(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_functor_type_constructor())
        fa = f(a)

        # Draw values
        v = data.draw(fa)
        x = data.draw(b)

        cls.assert_functor_replace(v, x, data=data)
        return
