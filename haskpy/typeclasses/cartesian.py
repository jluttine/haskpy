import attr
from hypothesis import given
from hypothesis import strategies as st

from .profunctor import Profunctor
from haskpy.utils import identity, assert_output
from haskpy import testing


class _CartesianMeta(type(Profunctor)):


    @assert_output
    def assert_cartesian_identity(cls, h):
        lunit = lambda a_1: a_1[0]
        runit = lambda a: (a, ())
        return (
            h.dimap(lunit, runit),
            h.first(),
        )


    @given(st.data())
    def test_cartesian_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        h = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cartesian_identity(
            h,
            data=data,
            input_strategy=st.tuples(st.integers(), st.just(())),
        )
        return


    @assert_output
    def assert_cartesian_associativity(cls, h):
        lassoc = lambda a_bc: ((a_bc[0], a_bc[1][0]), a_bc[1][1])
        rassoc = lambda ab_c: (ab_c[0][0], (ab_c[0][1], ab_c[1]))
        return (
            h.first().first().dimap(lassoc, rassoc),
            h.first(),
        )


    @given(st.data())
    def test_cartesian_associativity(cls, data):
        # Draw types
        a = st.tuples(
            data.draw(testing.sample_hashable_type()),
            st.tuples(
                st.just("foo"),
                st.just("bar"),
            )
        )
        b = data.draw(testing.sample_type())

        # Draw values
        h = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cartesian_associativity(h, data=data, input_strategy=a)
        return


    #
    # Test laws based on default implementations
    #


    @assert_output
    def assert_cartesian_first(cls, x):
        return (
            Cartesian.first(x),
            x.first(),
        )


    @given(st.data())
    def test_cartesian_first(cls, data):
        # Draw types
        a1 = data.draw(testing.sample_hashable_type())
        a2 = data.draw(testing.sample_hashable_type())
        a = st.tuples(a1, a2)
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cartesian_first(
            x,
            data=data,
            input_strategy=a,
        )
        return

    @assert_output
    def assert_cartesian_second(cls, x):
        return (
            Cartesian.second(x),
            x.second(),
        )


    @given(st.data())
    def test_cartesian_second(cls, data):
        # Draw types
        a1 = data.draw(testing.sample_hashable_type())
        a2 = data.draw(testing.sample_hashable_type())
        a = st.tuples(a1, a2)
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cartesian_second(
            x,
            data=data,
            input_strategy=a,
        )
        return


class Cartesian(Profunctor, metaclass=_CartesianMeta):
    """Cartesian profunctor

    Perhaps better known as Strong in Haskell:

    https://hackage.haskell.org/package/profunctors-5.2/docs/Data-Profunctor-Strong.html

    I decided to use name Cartesian because that was used in the profunctor
    optics paper.

    Minimal complete definition: ``first | second``.

    """


    def first(self):
        """p a b -> p (a, c) (b, c)"""
        return self.second().dimap(_flip_tuple, _flip_tuple)


    def second(self):
        """p a b -> p (c, a) (c, a)"""
        return self.first().dimap(_flip_tuple, _flip_tuple)


def _flip_tuple(ab):
    return (ab[1], ab[0])
