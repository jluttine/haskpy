from hypothesis import given
from hypothesis import strategies as st

from .typeclass import Type
from haskpy.utils import identity, assert_output, abstract_class_function
from haskpy import testing
from haskpy import utils


class Functor(Type):
    """Covariant functor

    Minimal complete definition:

    ..

        map

    For property tests:

    ..

        sample_functor_type

    Examples
    --------

    In Haskell, Map is a Functor, but not Applicative

    """

    @utils.abstract_function
    def map(self, f):
        """Haskell fmap"""

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
    def sample_functor_type(cls, a):
        pass

    #
    # Test typeclass laws
    #

    @utils.class_function
    @assert_output
    def assert_functor_identity(cls, v):
        return(
            v,
            v.map(identity),
        )

    @utils.class_function
    @given(st.data())
    def test_functor_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_functor_type(a))

        # Draw values
        v = data.draw(fa)

        cls.assert_functor_identity(v, data=data)
        return

    @utils.class_function
    @assert_output
    def assert_functor_composition(cls, v, f, g):
        return (
            v.map(f).map(g),
            v.map(lambda x: g(f(x))),
        )

    @utils.class_function
    @given(st.data())
    def test_functor_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        c = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_functor_type(a))

        # Draw values
        v = data.draw(fa)
        f = data.draw(testing.sample_function(b))
        g = data.draw(testing.sample_function(c))

        cls.assert_functor_composition(v, f, g, data=data)
        return

    #
    # Test laws based on default implementations
    #

    @utils.class_function
    @assert_output
    def assert_functor_map(cls, v, f):
        from haskpy.functions import map
        return (
            v.map(f),
            map(f, v),
        )

    @utils.class_function
    @given(st.data())
    def test_functor_map(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_functor_type(a))

        # Draw values
        v = data.draw(fa)
        f = data.draw(testing.sample_function(b))

        cls.assert_functor_map(v, f, data=data)
        return

    @utils.class_function
    @assert_output
    def assert_functor_replace(cls, v, x):
        from haskpy.functions import replace
        return (
            Functor.replace(v, x),
            replace(x, v),
            v.replace(x),
        )

    @utils.class_function
    @given(st.data())
    def test_functor_replace(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_functor_type(a))

        # Draw values
        v = data.draw(fa)
        x = data.draw(b)

        cls.assert_functor_replace(v, x, data=data)
        return


# Functor-related functions are defined in function module because of circular
# dependency.
