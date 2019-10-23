import attr
from hypothesis import given
from hypothesis import strategies as st

from .typeclass import TypeclassMeta
from haskpy.utils import identity


def _eq(map, x, y):
    return map(x) == map(y)


class _FunctorMeta(TypeclassMeta):


    @given(st.data())
    def test_functor_identity(cls, data):
        t = cls.assert_functor_identity
        t(data.draw(cls.sample(st.integers())))
        t(data.draw(cls.sample(st.dates())))
        t(data.draw(cls.sample(st.lists(st.integers()))))
        t(data.draw(cls.sample(cls.sample(st.integers()))))
        return


    @given(st.data())
    def test_functor_composition(cls, data):
        t = cls.assert_functor_composition
        t(
            data.draw(cls.sample(st.integers())),
            lambda x: x + 1,
            lambda x: x * 2,
        )
        t(
            data.draw(cls.sample(st.lists(st.dates()))),
            lambda x: x + x[::-1],
            lambda x: x * 2,
        )
        t(
            data.draw(cls.sample(cls.sample(st.integers()))),
            lambda x: x.map(lambda y: y + 1),
            lambda x: x.map(lambda y: y * 2),
        )
        return


    @given(st.data())
    def test_functor_map(cls, data):
        t = cls.assert_functor_map
        t(
            data.draw(cls.sample(st.integers())),
            lambda x: x + 42,
        )
        t(
            data.draw(cls.sample(st.lists(st.dates()))),
            lambda x: x + x[::-1],
        )
        t(
            data.draw(cls.sample(cls.sample(st.integers()))),
            lambda x: x.map(lambda y: y * 2),
        )
        return


    @given(st.data())
    def test_functor_replace(cls, data):
        t = cls.assert_functor_replace
        t(
            data.draw(cls.sample(st.integers())),
            data.draw(st.dates()),
        )
        t(
            data.draw(cls.sample(cls.sample(st.dates()))),
            data.draw(st.integers()),
        )
        return


    def assert_functor_identity(cls, v, eqmap=identity):
        assert _eq(eqmap, v.map(identity), v)
        return


    def assert_functor_composition(cls, v, f, g, eqmap=identity):
        assert _eq(eqmap, v.map(lambda x: g(f(x))), v.map(f).map(g))
        return


    def assert_functor_map(cls, v, f, eqmap=identity):
        from haskpy.functions import map
        assert _eq(eqmap, map(f, v), v.map(f))
        return


    def assert_functor_replace(cls, v, x, eqmap=identity):
        from haskpy.functions import replace
        assert _eq(eqmap, Functor.replace(v, x), replace(x, v))
        assert _eq(eqmap, Functor.replace(v, x), v.replace(x))
        return


@attr.s(frozen=True)
class Functor(metaclass=_FunctorMeta):
    """Covariant functor"""


    def map(self, f):
        """Haskell fmap"""
        raise NotImplementedError()


    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)


# Functor-related functions are defined in function module because of circular
# dependency.
