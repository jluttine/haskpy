import attr
from hypothesis import given
from hypothesis import strategies as st

from .profunctor import Profunctor
from haskpy.utils import identity, assert_output
from haskpy import testing


class _CocartesianMeta(type(Profunctor)):
    pass


    # def sample_type(cls):
    #     a = testing.sample_type()
    #     b = testing.sample_type()
    #     return st.tuples(a, b).map(lambda ab: cls.sample_profunctor_value(a, b))


    # def sample_profunctor_value(cls, a, b):
    #     return cls.sample_value(a, b)


    # @st.composite
    # def sample_contravariant_value(draw, cls, a):
    #     b = draw(testing.sample_type())
    #     return draw(cls.sample_profunctor_value(a, b))


    # @st.composite
    # def sample_functor_value(draw, cls, b):
    #     a = draw(testing.sample_type())
    #     return draw(cls.sample_profunctor_value(a, b))

    #
    # Test typeclass laws
    #


    # @assert_output
    # def assert_profunctor_identity(cls, x):
    #     return (
    #         x,
    #         x.dimap(identity, identity),
    #     )


    # @given(st.data())
    # def test_profunctor_identity(cls, data):
    #     # Draw types
    #     a = data.draw(testing.sample_hashable_type())
    #     b = data.draw(testing.sample_type())

    #     # Draw values
    #     x = data.draw(cls.sample_profunctor_value(a, b))

    #     cls.assert_profunctor_identity(x, data=data)
    #     return


    # #
    # # Test laws based on default implementations
    # #


    # @assert_output
    # def assert_profunctor_dimap(cls, x, f, g):
    #     from haskpy.functions import dimap
    #     return (
    #         Profunctor.dimap(x, f, g),
    #         x.dimap(f, g),
    #         dimap(f, g, x),
    #     )


    # @given(st.data())
    # def test_profunctor_dimap(cls, data):
    #     # Draw types
    #     b = data.draw(testing.sample_hashable_type())
    #     c = data.draw(testing.sample_hashable_type())
    #     d = data.draw(testing.sample_type())

    #     # Draw values
    #     x = data.draw(cls.sample_profunctor_value(b, c))
    #     f = data.draw(testing.sample_function(b))
    #     g = data.draw(testing.sample_function(d))

    #     cls.assert_profunctor_dimap(x, f, g, data=data)
    #     return


    # @assert_output
    # def assert_profunctor_map(cls, x, f):
    #     return (
    #         Profunctor.map(x, f),
    #         x.map(f),
    #     )


    # @given(st.data())
    # def test_profunctor_map(cls, data):
    #     # Draw types
    #     b = data.draw(testing.sample_hashable_type())
    #     c = data.draw(testing.sample_hashable_type())
    #     d = data.draw(testing.sample_type())

    #     # Draw values
    #     x = data.draw(cls.sample_profunctor_value(b, c))
    #     g = data.draw(testing.sample_function(d))

    #     cls.assert_profunctor_map(x, g, data=data)
    #     return


    # @assert_output
    # def assert_profunctor_contramap(cls, x, f):
    #     return (
    #         Profunctor.contramap(x, f),
    #         x.contramap(f),
    #     )


    # @given(st.data())
    # def test_profunctor_contramap(cls, data):
    #     # Draw types
    #     b = data.draw(testing.sample_hashable_type())
    #     d = data.draw(testing.sample_type())

    #     # Draw values
    #     x = data.draw(cls.sample_profunctor_value(b, d))
    #     f = data.draw(testing.sample_function(b))

    #     cls.assert_profunctor_contramap(x, f, data=data)
    #     return


@attr.s(frozen=True)
class Cocartesian(Profunctor, metaclass=_CocartesianMeta):
    """Cocartesian profunctor

    Perhaps better known as Choice in Haskell:

    https://hackage.haskell.org/package/profunctors-5.2/docs/Data-Profunctor-Choice.html

    I decided to use name Cocartesian because that was used in the profunctor
    optics paper.

    Minimal complete definition: ``left | right``.

    """


    def left(self):
        return self.dimap(_flip_either, _flip_either).right()


    def right(self):
        return self.dimap(_flip_either, _flip_either).left()


def _flip_either(x):
    return x.match(
        Left=lambda a: Right(a),
        Right=lambda b: Left(b),
    )


# Profunctor-related functions are defined in function module because of
# circular dependency.
