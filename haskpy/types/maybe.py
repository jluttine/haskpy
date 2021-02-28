import attr
import hypothesis.strategies as st

from haskpy.typeclasses import (
    Monad,
    Commutative,
    Monoid,
    Hashable,
    Foldable,
    Eq,
)
from haskpy.utils import (
    immutable,
    class_function,
    class_property,
    eq_test,
)

from haskpy import testing


@immutable
class Maybe(
        Monad,
        Commutative,
        Monoid,
        Hashable,
        Foldable,
        Eq,
):
    """Maybe type for optional values"""

    match = attr.ib()

    @class_property
    def empty(cls):
        return Nothing

    @class_function
    def pure(cls, x):
        return Just(x)

    def map(self, f):
        return self.match(
            Nothing=lambda: Nothing,
            Just=lambda x: Just(f(x)),
        )

    def apply_to(self, x):
        return self.match(
            Nothing=lambda: Nothing,
            Just=lambda f: x.map(f),
        )

    def bind(self, f):
        return self.match(
            Nothing=lambda: Nothing,
            Just=lambda x: f(x),
        )

    def append(self, m):
        return self.match(
            Nothing=lambda: m,
            Just=lambda x: m.match(
                Nothing=lambda: self,
                Just=lambda y: Just(x.append(y)),
            ),
        )

    def fold_map(self, monoid, f):
        return self.match(
            Nothing=lambda: monoid.empty,
            Just=lambda x: f(x),
        )

    def foldl(self, combine, initial):
        return self.match(
            Nothing=lambda: initial,
            Just=lambda x: combine(initial)(x),
        )

    def foldr(self, combine, initial):
        return self.match(
            Nothing=lambda: initial,
            Just=lambda x: combine(x)(initial),
        )

    def length(self):
        return self.match(
            Nothing=lambda: 0,
            Just=lambda _: 1,
        )

    def to_iter(self):
        yield from self.match(
            Nothing=lambda: (),
            Just=lambda x: (x,),
        )

    def __repr__(self):
        return self.match(
            Nothing=lambda: "Nothing",
            Just=lambda x: "Just({0})".format(repr(x)),
        )

    def __eq__(self, other):
        return self.match(
            Nothing=lambda: other.match(
                Nothing=lambda: True,
                Just=lambda _: False,
            ),
            Just=lambda x: other.match(
                Nothing=lambda: False,
                Just=lambda y: x == y,
            ),
        )

    def __eq_test__(self, other, data):
        return self.match(
            Nothing=lambda: other.match(
                Nothing=lambda: True,
                Just=lambda _: False,
            ),
            Just=lambda x: other.match(
                Nothing=lambda: False,
                Just=lambda y: eq_test(x, y, data),
            ),
        )

    #
    # Sampling methods for property tests
    #

    @class_function
    def sample_value(cls, a):
        return st.one_of(st.just(Nothing), a.map(Just))

    sample_type = testing.sample_type_from_value(
        testing.sample_type(),
    )

    sample_functor_type = testing.sample_type_from_value()
    sample_applicative_type = sample_functor_type
    sample_monad_type = sample_functor_type

    sample_hashable_type = testing.sample_type_from_value(
        testing.sample_hashable_type(),
    )

    sample_semigroup_type = testing.sample_type_from_value(
        testing.sample_semigroup_type(),
    )
    sample_monoid_type = sample_semigroup_type

    sample_commutative_type = testing.sample_type_from_value(
        testing.sample_commutative_type(),
    )

    sample_eq_type = testing.sample_type_from_value(
        testing.sample_commutative_type(),
    )

    sample_foldable_type = testing.sample_type_from_value()
    sample_foldable_functor_type = sample_foldable_type


Nothing = Maybe(lambda *, Nothing, Just: Nothing())


def Just(x):
    return Maybe(lambda *, Nothing, Just: Just(x))


def MaybeT(M):
    """m (Maybe a) -> MaybeT m a"""

    # NOTE: It might be tempting to use Compose as a basis for this kind of
    # Monad transformers. Indeed, it seems like these are just monadic
    # extensions to the composition that can be written only for Applicatives
    # in generic form. However, that is not the case. See an example in
    # test_maybe.py on how MaybeT isn't a monadic extension of Compose but
    # rather its Applicative instance is different from that of Compose. This
    # is rather interesting as it's a common misconception that the common
    # monad transformers are monadic extensions of Compose. Even "Learn Haskell
    # programming from first principles" introduces monad transformers in such
    # a way that it leads to that kind of understanding.

    class MetaMaybeM(type(Monad)):

        def __repr__(cls):
            return "MaybeT({})".format(repr(M))

    @immutable
    class MaybeM(Monad, Eq, metaclass=MetaMaybeM):

        # The attribute name may sound weird but it makes sense once you
        # understand that this indeed is the not-yet-composed variable and if
        # you want to decompose a composed variable you get it by x.decomposed.
        # Thus, there's no need to write a simple function to just return this
        # attribute, just use this directly.
        decomposed = attr.ib()

        @class_function
        def pure(cls, x):
            """a -> MaybeT m a"""
            return cls(M.pure(Maybe.pure(x)))

        def bind(self, f):
            """MaybeT m a -> (a -> MaybeT m b) -> MaybeT m b

            In decompressed terms:

              m (Maybe a) -> (a -> m (Maybe b)) -> m (Maybe b)

            """

            # :: m (Maybe a)
            mMa = self.decomposed

            # :: Maybe a -> m (Maybe b)
            def g(Ma):
                return Ma.match(
                    Nothing=lambda: M.pure(Nothing),
                    Just=lambda x: f(x).decomposed,
                )

            # :: MaybeT m b
            return MaybeM(mMa.bind(g))

        def __eq__(self, other):
            return self.decomposed == other.decomposed

        def __repr__(self):
            return "{0}({1})".format(repr(MaybeM), repr(self.decomposed))

        def __eq_test__(self, other, data):
            return eq_test(self.decomposed, other.decomposed, data)

        @class_function
        def sample_value(cls, a):
            return M.sample_value(Maybe.sample_value(a)).map(cls)

        sample_type = testing.sample_type_from_value(
            testing.sample_type(),
        )

        sample_functor_type = testing.sample_type_from_value()
        sample_applicative_type = sample_functor_type
        sample_monad_type = sample_functor_type

        sample_eq_type = testing.sample_type_from_value(
            testing.sample_eq_type(),
        )

    return MaybeM
