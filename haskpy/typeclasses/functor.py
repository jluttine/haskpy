import attr
from hypothesis import given
from hypothesis import strategies as st

from .typeclass import Type
from haskpy.utils import identity, assert_output
from haskpy import testing


class _FunctorMeta(type(Type)):


    def sample_type(cls):
        t = testing.sample_type()
        return t.map(cls.sample_functor_value)


    def sample_functor_value(cls, a):
        return cls.sample_value(a)


    #
    # Test typeclass laws
    #


    @assert_output
    def assert_functor_identity(cls, v):
        return(
            v,
            v.map(identity),
        )


    @given(st.data())
    def test_functor_identity(cls, data):
        t = data.draw(cls.sample_type())
        cls.assert_functor_identity(
            data.draw(t),
            data=data
        )
        return


    @assert_output
    def assert_functor_composition(cls, v, f, g):
        return (
            v.map(f).map(g),
            v.map(lambda x: g(f(x))),
        )


    @given(st.data())
    def test_functor_composition(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_hashable_type())
        c = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))
        f = data.draw(testing.sample_function(b))
        g = data.draw(testing.sample_function(c))

        cls.assert_functor_composition(v, f, g, data=data)
        return


    #
    # Test laws based on default implementations
    #


    @assert_output
    def assert_functor_map(cls, v, f):
        from haskpy.functions import map
        return (
            v.map(f),
            map(f, v),
        )


    @given(st.data())
    def test_functor_map(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))
        f = data.draw(testing.sample_function(b))

        cls.assert_functor_map(v, f, data=data)
        return


    @assert_output
    def assert_functor_replace(cls, v, x):
        from haskpy.functions import replace
        return (
            Functor.replace(v, x),
            replace(x, v),
            v.replace(x),
        )


    @given(st.data())
    def test_functor_replace(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        v = data.draw(cls.sample_functor_value(a))
        x = data.draw(b)

        cls.assert_functor_replace(v, x, data=data)
        return


class Functor(Type, metaclass=_FunctorMeta):
    """Covariant functor"""


    def map(self, f):
        """Haskell fmap"""
        raise NotImplementedError()


    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)


# Functor-related functions are defined in function module because of circular
# dependency.
