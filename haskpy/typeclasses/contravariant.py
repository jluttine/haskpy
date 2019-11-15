import attr
from hypothesis import given
from hypothesis import strategies as st

from .typeclass import Type
from haskpy.utils import identity, assert_output
from haskpy import testing


class _ContravariantMeta(type(Type)):


    def sample_type(cls):
        t = testing.sample_type()
        return t.map(cls.sample_contravariant_value)


    def sample_contravariant_value(cls, a):
        return cls.sample_value(a)


    #
    # Test typeclass laws
    #


    @assert_output
    def assert_contravariant_identity(cls, v):
        return(
            v,
            v.contramap(identity),
        )


    @given(st.data())
    def test_contravariant_identity(cls, data):
        t = data.draw(cls.sample_type())
        cls.assert_contravariant_identity(
            data.draw(t),
            data=data
        )
        return


    @assert_output
    def assert_contravariant_composition(cls, v, f, g):
        return (
            v.contramap(f).contramap(g),
            v.contramap(lambda x: f(g(x))),
        )


    @given(st.data())
    def test_contravariant_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_hashable_type())
        c = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_contravariant_value(a))
        f = data.draw(testing.sample_function(b))
        g = data.draw(testing.sample_function(c))

        cls.assert_contravariant_composition(v, f, g, data=data)
        return


    #
    # Test laws based on default implementations
    #


    @assert_output
    def assert_contravariant_contramap(cls, v, f):
        from haskpy.functions import contramap
        return (
            v.contramap(f),
            contramap(f, v),
        )


    @given(st.data())
    def test_contravariant_contramap(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_contravariant_value(a))
        f = data.draw(testing.sample_function(b))

        cls.assert_contravariant_contramap(v, f, data=data)
        return


    @assert_output
    def assert_contravariant_contrareplace(cls, v, x):
        from haskpy.functions import contrareplace
        return (
            Contravariant.contrareplace(v, x),
            contrareplace(x, v),
            v.contrareplace(x),
        )


    @given(st.data())
    def test_contravariant_contrareplace(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_contravariant_value(a))
        x = data.draw(b)

        cls.assert_contravariant_contrareplace(v, x, data=data)
        return


class Contravariant(Type, metaclass=_ContravariantMeta):
    """Contravariant functor

    Minimal complete definition:

    - ``contramap`` method

    """


    def contramap(self, f):
        """f b -> (a -> b) -> f a"""
        raise NotImplementedError()


    def contrareplace(self, x):
        """f b -> b -> f a"""
        return self.contramap(lambda _: x)


# Contravariant-related functions are defined in function module because of
# circular dependency.
