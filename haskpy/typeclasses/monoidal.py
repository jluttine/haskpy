import attr
from hypothesis import given
from hypothesis import strategies as st

from .profunctor import Profunctor
from haskpy.utils import identity, assert_output
from haskpy import testing


class _MonoidalMeta(type(Profunctor)):


    @property
    def punit(cls):
        """p () ()"""
        raise NotImplementedError()


    # @assert_output
    # def assert_cartesian_identity(cls, h):
    #     lunit = lambda a_1: a_1[0]
    #     runit = lambda a: (a, ())
    #     return (
    #         h.dimap(lunit, runit),
    #         h.first(),
    #     )


    # @given(st.data())
    # def test_cartesian_identity(cls, data):
    #     # Draw types
    #     a = data.draw(testing.sample_hashable_type())
    #     b = data.draw(testing.sample_type())

    #     # Draw values
    #     h = data.draw(cls.sample_profunctor_value(a, b))

    #     cls.assert_cartesian_identity(
    #         h,
    #         data=data,
    #         input_strategy=st.tuples(st.integers(), st.just(())),
    #     )
    #     return


    # @assert_output
    # def assert_cartesian_associativity(cls, h):
    #     lassoc = lambda a_bc: ((a_bc[0], a_bc[1][0]), a_bc[1][1])
    #     rassoc = lambda ab_c: (ab_c[0][0], (ab_c[0][1], ab_c[1][0]))
    #     return (
    #         h.first().first().dimap(lassoc, rassoc),
    #         h.first(),
    #     )


    # @given(st.data())
    # def test_cartesian_associativity(cls, data):
    #     # Draw types
    #     a = data.draw(
    #         st.tuples(
    #             testing.sample_hashable_type(),
    #             st.tuples(
    #                 st.just("foo"),
    #                 st.just("bar"),
    #             )
    #         )
    #     )
    #     b = data.draw(testing.sample_type())

    #     # Draw values
    #     h = data.draw(cls.sample_profunctor_value(a, b))

    #     cls.assert_cartesian_associativity(h, data=data, input_strategy=a)
    #     return


    # #
    # # Test laws based on default implementations
    # #


    # @assert_output
    # def assert_cartesian_first(cls, x):
    #     return (
    #         Cartesian.first(x),
    #         x.first(),
    #     )


    # @given(st.data())
    # def test_cartesian_first(cls, data):
    #     # Draw types
    #     a1 = data.draw(testing.sample_hashable_type())
    #     a2 = data.draw(testing.sample_hashable_type())
    #     a = st.tuples(a1, a2)
    #     b = data.draw(testing.sample_type())

    #     # Draw values
    #     x = data.draw(cls.sample_profunctor_value(a, b))

    #     cls.assert_cartesian_first(
    #         x,
    #         data=data,
    #         input_strategy=a,
    #     )
    #     return

    # @assert_output
    # def assert_cartesian_second(cls, x):
    #     return (
    #         Cartesian.second(x),
    #         x.second(),
    #     )


    # @given(st.data())
    # def test_cartesian_second(cls, data):
    #     # Draw types
    #     a1 = data.draw(testing.sample_hashable_type())
    #     a2 = data.draw(testing.sample_hashable_type())
    #     a = st.tuples(a1, a2)
    #     b = data.draw(testing.sample_type())

    #     # Draw values
    #     x = data.draw(cls.sample_profunctor_value(a, b))

    #     cls.assert_cartesian_second(
    #         x,
    #         data=data,
    #         input_strategy=a,
    #     )
    #     return


class Monoidal(Profunctor, metaclass=_MonoidalMeta):
    """Monoidal profunctor

    Minimal complete definition: ``punit & par``.

    """


    def par(self, p):
        """p a b -> p c d -> p (a, b) (c, d)

        Parallel application of two profunctors.

        """
        raise NotImplementedError()
