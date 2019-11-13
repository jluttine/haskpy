import hypothesis.strategies as st
import attr

from haskpy.typeclasses import Cartesian
from haskpy import testing
from haskpy.functions import function


class _LensMeta(type(Cartesian)):


    def sample_value(cls, a, b, s, t):
        v = testing.sample_function(a)
        u = testing.sample_function(t)
        return st.tuples(v, u).map(lambda vu: cls(vu[0], vu[1]))


    @st.composite
    def sample_profunctor_value(draw, cls, s, t):
        a = draw(testing.sample_hashable_type())
        b = draw(testing.sample_type())
        return draw(cls.sample_value(a, b, s, t))


@attr.s(frozen=True, cmp=False, repr=False)
class Lens(Cartesian, metaclass=_LensMeta):


    __view = attr.ib()


    __update = attr.ib()


    def dimap(self, f, g):
        return Lens(
            lambda xs: self.__view(f(xs)),
            lambda x_xs: g(self.__update((x_xs[0], f(x_xs[1])))),
        )


    def first(self):
        return Lens(
            lambda xs: self.__view(xs[0]),
            lambda x_xs: (self.__update((x_xs[0], x_xs[1][0])), x_xs[1][1]),
        )


    def second(self):
        return Lens(
            lambda xs: self.__view(xs[1]),
            lambda x_xs: (x_xs[1][0], self.__update((x_xs[0], x_xs[1][1]))),
        )


    def __test_eq__(self, g, data, input_strategy=st.integers()):
        # NOTE: This is used only in tests when the function input doesn't
        # really matter so any hashable type here is ok. The type doesn't
        # matter because the functions are either _TestFunction or created with
        # pure.
        a = data.draw(st.integers())
        s = data.draw(input_strategy)
        v = self.__view(s) == g.__view(s)
        u = self.__update((a, s)) == g.__update((a, s))
        return v and u


@function
def lens(view, update):
    """(s -> a) -> ((b, s) -> t) -> LensP a b s t

    where

    type LensP a b s t = Cartesian p => p a b -> p s t

    Create a profunctor lens and apply it to p. You probably want to partially
    evaluate this function by giving only view and update in order to construct
    a profunctor lens.

    """

    def run(p):
        """LensP a b s t

        that is,

        Cartesian p => p a b -> p s t

        """

        # For convenience, if we are given a plain Python function, let's wrap it
        # with our function decorator to get all the Profunctor goodies
        # automatically without the user needing to add the wrapping explicitly.
        # Just a usability improvement.
        if isinstance(p, type(lambda: 42)):
            p = function(p)

        return p.first().dimap(lambda x: (view(x), x), update)

    return run
