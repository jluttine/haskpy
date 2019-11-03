import attr
from hypothesis import given
from hypothesis import strategies as st

from .typeclass import Type
from haskpy.utils import identity, assert_output


class _FunctorMeta(type(Type)):


    def sample_functor(cls, elements):
        # By default, assume the class is a one-argument type constructor
        return cls.sample(elements)


    @assert_output
    def assert_functor_identity(cls, v):
        return(
            v,
            v.map(identity),
        )


    @given(st.data())
    def test_functor_identity(cls, data):
        cls.assert_functor_identity(
            data.draw(cls.sample()),
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
        t = cls.assert_functor_composition
        t(
            data.draw(cls.sample_functor(st.integers())),
            lambda x: x + 1,
            lambda x: x * 2,
            data=data
        )
        t(
            data.draw(cls.sample_functor(st.lists(st.dates()))),
            lambda x: x + x[::-1],
            lambda x: x * 2,
            data=data
        )
        t(
            data.draw(cls.sample_functor(cls.sample_functor(st.integers()))),
            lambda x: x.map(lambda y: y + 1),
            lambda x: x.map(lambda y: y * 2),
            data=data
        )
        return


    @assert_output
    def assert_functor_map(cls, v, f):
        from haskpy.functions import map
        return (
            v.map(f),
            map(f, v),
        )


    @given(st.data())
    def test_functor_map(cls, data):
        t = cls.assert_functor_map
        t(
            data.draw(cls.sample_functor(st.integers())),
            lambda x: x + 42,
            data=data
        )
        t(
            data.draw(cls.sample_functor(st.lists(st.dates()))),
            lambda x: x + x[::-1],
            data=data
        )
        t(
            data.draw(cls.sample_functor(cls.sample_functor(st.integers()))),
            lambda x: x.map(lambda y: y * 2),
            data=data
        )
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
        cls.assert_functor_replace(
            data.draw(cls.sample()),
            data.draw(st.one_of(st.integers(), st.dates())),
            data=data
        )
        return


@attr.s(frozen=True)
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
