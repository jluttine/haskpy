"""Values with two possibilities

.. autosummary::
   :toctree:

   Either
   Left
   Right
   either
   is_left
   is_right
   from_left
   from_right
   left
   right

"""

import attr
import hypothesis.strategies as st

from haskpy.typeclasses import Monad, Eq
from haskpy.internal import class_function, immutable

from haskpy.optics import prism

from haskpy.testing import eq_test
from haskpy import testing
from haskpy.types.function import function


@immutable
class Either(Monad, Eq):

    match = attr.ib()

    @class_function
    def pure(cls, x):
        return Right(x)

    def map(self, f):
        return self.match(
            Left=lambda _: self,
            Right=lambda x: Right(f(x)),
        )

    def apply_to(self, x):
        return self.match(
            Left=lambda _: self,
            Right=lambda f: x.map(f),
        )

    def bind(self, f):
        return self.match(
            Left=lambda _: self,
            Right=lambda x: f(x),
        )

    def __eq__(self, other):
        return self.match(
            Left=lambda x: other.match(
                Left=lambda y: x == y,
                Right=lambda _: False,
            ),
            Right=lambda x: other.match(
                Left=lambda _: False,
                Right=lambda y: x == y,
            ),
        )

    def __eq_test__(self, other, data):
        return self.match(
            Left=lambda x: other.match(
                Left=lambda y: eq_test(x, y, data=data),
                Right=lambda _: False,
            ),
            Right=lambda x: other.match(
                Left=lambda _: False,
                Right=lambda y: eq_test(x, y, data=data),
            ),
        )

    def __repr__(self):
        return self.match(
            Left=lambda x: "Left({0})".format(repr(x)),
            Right=lambda x: "Right({0})".format(repr(x)),
        )

    @class_function
    def sample_value(cls, a, b):
        return st.one_of(a.map(Left), b.map(Right))

    sample_type = testing.create_type_sampler(
        testing.sample_type(),
        testing.sample_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler(
        testing.sample_type(),
    )

    # Some typeclass instances have constraints for the types inside

    sample_eq_type = testing.create_type_sampler(
        testing.sample_eq_type(),
        testing.sample_eq_type(),
    )


def Left(x):
    return Either(lambda *, Left, Right: Left(x))


def Right(x):
    return Either(lambda *, Left, Right: Right(x))


@function
def either(f, g, e):
    """(a -> c) -> (b -> c) -> Either a b -> c"""
    return e.match(Left=f, Right=g)


@function
def is_left(m):
    return m.match(
        Left=lambda _: True,
        Right=lambda _: False,
    )


@function
def is_right(m):
    return m.match(
        Left=lambda _: False,
        Right=lambda _: True,
    )


@function
def from_left(x, e):
    return e.match(
        Left=lambda y: y,
        Right=lambda _: x,
    )


@function
def from_right(x, e):
    return e.match(
        Left=lambda _: x,
        Right=lambda y: y,
    )


#
# Optics
#


left = prism(
    lambda m: m.match(
        Left=lambda x: Right(x),
        Right=lambda _: Left(m),
    ),
    lambda x: Left(x),
)


right = prism(
    lambda m: m.match(
        Left=lambda _: Left(m),
        Right=lambda x: Right(x),
    ),
    lambda x: Right(x),
)
