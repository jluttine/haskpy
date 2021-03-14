from hypothesis import given
from hypothesis import strategies as st

from haskpy.internal import class_function, abstract_class_function
from haskpy.testing import assert_output
from haskpy import testing

# Use the "hidden" module in order to avoid circular imports
from ._profunctor import Profunctor


class Cocartesian(Profunctor):
    """Cocartesian profunctor

    Perhaps better known as Choice in Haskell:

    https://hackage.haskell.org/package/profunctors-5.2/docs/Data-Profunctor-Choice.html

    I decided to use name Cocartesian because that was used in the profunctor
    optics paper.

    Minimal complete definition: ``left | right``.

    """

    def left(self):
        return self.right().dimap(_flip_either, _flip_either)

    def right(self):
        return self.left().dimap(_flip_either, _flip_either)

    @abstract_class_function
    def sample_cocartesian_type_constructor(cls):
        """Sample a cocartesian type constructor

        By default, :py:meth:`.Profunctor.sample_profunctor_type_constructor`
        is used. If Cocartesian type requires more constraints than Profunctor
        type, override this default implementation.

        """
        return cls.sample_profunctor_type_constructor()

    #
    # Test Cocartesian laws
    #

    @class_function
    @assert_output
    def assert_cocartesian_unit(cls, h):
        from haskpy import Left
        lzero = lambda ea: ea.match(Left=lambda a: a, Right=lambda _: None)
        rzero = lambda a: Left(a)
        return (
            h.dimap(lzero, rzero),
            h.left(),
        )

    @class_function
    @given(st.data())
    def test_cocartesian_unit(cls, data):
        from haskpy import Left
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cocartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        h = data.draw(fab)

        cls.assert_cocartesian_unit(
            h,
            data=data,
            input_strategy=a.map(Left),
        )
        return

    @class_function
    @assert_output
    def assert_cocartesian_associativity(cls, h):
        from haskpy.types.either import Left, Right
        lcoassoc = lambda a_bc: a_bc.match(
            Left=lambda a: Left(Left(a)),
            Right=lambda bc: bc.match(
                Left=lambda b: Left(Right(b)),
                Right=lambda c: Right(c)
            )
        )
        rcoassoc = lambda ab_c: ab_c.match(
            Left=lambda ab: ab.match(
                Left=lambda a: Left(a),
                Right=lambda b: Right(Left(b)),
            ),
            Right=lambda c: Right(Right(c))
        )
        return (
            h.left().left().dimap(lcoassoc, rcoassoc),
            h.left(),
        )

    @class_function
    @given(st.data())
    def test_cocartesian_associativity(cls, data):
        from haskpy.types.either import Either
        # Draw types
        a = Either.sample_value(
            data.draw(testing.sample_eq_type()),
            Either.sample_value(
                st.just("foo"),
                st.just("bar"),
            )
        )
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cocartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        h = data.draw(fab)

        cls.assert_cocartesian_associativity(h, data=data, input_strategy=a)
        return

    #
    # Test laws based on default implementations
    #

    @class_function
    @assert_output
    def assert_cocartesian_left(cls, x):
        return (
            Cocartesian.left(x),
            x.left(),
        )

    @class_function
    @given(st.data())
    def test_cocartesian_left(cls, data):
        from haskpy.types.either import Either
        # Draw types
        a1 = data.draw(testing.sample_eq_type())
        a2 = data.draw(testing.sample_eq_type())
        a = Either.sample_value(a1, a2)
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cocartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        x = data.draw(fab)

        cls.assert_cocartesian_left(
            x,
            data=data,
            input_strategy=a,
        )
        return

    @class_function
    @assert_output
    def assert_cocartesian_right(cls, x):
        return (
            Cocartesian.right(x),
            x.right(),
        )

    @class_function
    @given(st.data())
    def test_cocartesian_right(cls, data):
        from haskpy.types.either import Either
        # Draw types
        a1 = data.draw(testing.sample_eq_type())
        a2 = data.draw(testing.sample_eq_type())
        a = Either.sample_value(a1, a2)
        b = data.draw(testing.sample_type())
        f = data.draw(cls.sample_cocartesian_type_constructor())
        fab = f(a, b)

        # Draw values
        x = data.draw(fab)

        cls.assert_cocartesian_right(
            x,
            data=data,
            input_strategy=a,
        )
        return


def _flip_either(x):
    from haskpy.types.either import Left, Right
    return x.match(
        Left=lambda a: Right(a),
        Right=lambda b: Left(b),
    )
