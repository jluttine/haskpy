import attr
from hypothesis import given
from hypothesis import strategies as st

from .profunctor import Profunctor
from haskpy.utils import identity, assert_output
from haskpy import testing


class _CocartesianMeta(type(Profunctor)):


    @assert_output
    def assert_cocartesian_unit(cls, h):
        from haskpy.types import Left
        lzero = lambda ea: ea.match(Left=lambda a: a, Right=lambda _: None)
        rzero = lambda a: Left(a)
        return (
            h.dimap(lzero, rzero),
            h.left(),
        )


    @given(st.data())
    def test_cocartesian_unit(cls, data):
        from haskpy.types import Either, Left
        # Draw types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_type())

        # Draw values
        h = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cocartesian_unit(
            h,
            data=data,
            input_strategy=a.map(Left),
        )
        return


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


    @given(st.data())
    def test_cocartesian_associativity(cls, data):
        from haskpy.types.either import Either
        # Draw types
        a = Either.sample_value(
            data.draw(testing.sample_hashable_type()),
            Either.sample_value(
                st.just("foo"),
                st.just("bar"),
            )
        )
        b = data.draw(testing.sample_type())

        # Draw values
        h = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cocartesian_associativity(h, data=data, input_strategy=a)
        return


    #
    # Test laws based on default implementations
    #


    @assert_output
    def assert_cocartesian_left(cls, x):
        return (
            Cocartesian.left(x),
            x.left(),
        )


    @given(st.data())
    def test_cocartesian_left(cls, data):
        from haskpy.types.either import Either
        # Draw types
        a1 = data.draw(testing.sample_hashable_type())
        a2 = data.draw(testing.sample_hashable_type())
        a = Either.sample_value(a1, a2)
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cocartesian_left(
            x,
            data=data,
            input_strategy=a,
        )
        return

    @assert_output
    def assert_cocartesian_right(cls, x):
        return (
            Cocartesian.right(x),
            x.right(),
        )


    @given(st.data())
    def test_cocartesian_right(cls, data):
        from haskpy.types.either import Either
        # Draw types
        a1 = data.draw(testing.sample_hashable_type())
        a2 = data.draw(testing.sample_hashable_type())
        a = Either.sample_value(a1, a2)
        b = data.draw(testing.sample_type())

        # Draw values
        x = data.draw(cls.sample_profunctor_value(a, b))

        cls.assert_cocartesian_right(
            x,
            data=data,
            input_strategy=a,
        )
        return


class Cocartesian(Profunctor, metaclass=_CocartesianMeta):
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


def _flip_either(x):
    from haskpy.types.either import Left, Right
    return x.match(
        Left=lambda a: Right(a),
        Right=lambda b: Left(b),
    )
