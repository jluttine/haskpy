from hypothesis import given
from hypothesis import strategies as st

from haskpy.internal import class_function
from haskpy.testing import assert_output
from haskpy import testing

# Use the "hidden" module in order to avoid circular imports
from ._profunctor import Profunctor


class Cartesian(Profunctor):
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

    @class_function
    def sample_cartesian_type_constructor(cls):
        """Sample a cartesian type constructor

        By default, :py:meth:`.Profunctor.sample_profunctor_type_constructor`
        is used. If Cartesian type requires more constraints than Profunctor
        type, override this default implementation.

        """
        return cls.sample_profunctor_type_constructor()

    #
    # Test Cartesian laws
    #

    @class_function
    @assert_output
    def assert_cartesian_identity(cls, h):
        lunit = lambda a_1: a_1[0]
        runit = lambda a: (a, ())
        return (
            h.dimap(lunit, runit),
            h.first(),
        )

    @class_function
    @given(st.data())
    def test_cartesian_identity(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        h = data.draw(fab)

        cls.assert_cartesian_identity(
            h,
            data=data,
            input_strategy=st.tuples(st.integers(), st.just(())),
        )
        return

    @class_function
    @assert_output
    def assert_cartesian_associativity(cls, h):
        lassoc = lambda a_bc: ((a_bc[0], a_bc[1][0]), a_bc[1][1])
        rassoc = lambda ab_c: (ab_c[0][0], (ab_c[0][1], ab_c[1]))
        return (
            h.first().first().dimap(lassoc, rassoc),
            h.first(),
        )

    @class_function
    @given(st.data())
    def test_cartesian_associativity(cls, data):
        # Draw types
        a = st.tuples(
            data.draw(testing.sample_eq_type()),
            st.tuples(
                st.just("foo"),
                st.just("bar"),
            )
        )
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        h = data.draw(fab)

        cls.assert_cartesian_associativity(h, data=data, input_strategy=a)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_cartesian_first(cls, x):
        return (
            Cartesian.first(x),
            x.first(),
        )

    @class_function
    @given(st.data())
    def test_cartesian_first(cls, data):
        # Draw types
        a1 = data.draw(testing.sample_eq_type())
        a2 = data.draw(testing.sample_eq_type())
        a = st.tuples(a1, a2)
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        x = data.draw(fab)

        cls.assert_cartesian_first(
            x,
            data=data,
            input_strategy=a,
        )
        return

    @class_function
    @assert_output
    def assert_cartesian_second(cls, x):
        return (
            Cartesian.second(x),
            x.second(),
        )

    @class_function
    @given(st.data())
    def test_cartesian_second(cls, data):
        # Draw types
        a1 = data.draw(testing.sample_eq_type())
        a2 = data.draw(testing.sample_eq_type())
        a = st.tuples(a1, a2)
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        x = data.draw(fab)

        cls.assert_cartesian_second(
            x,
            data=data,
            input_strategy=a,
        )
        return


def _flip_tuple(ab):
    return (ab[1], ab[0])
