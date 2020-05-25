import attr
import hypothesis.strategies as st

from haskpy.typeclasses import (
    Monad,
    CommutativeMonoid,
    Hashable,
    Foldable,
    Eq,
)
from haskpy.utils import (
    singleton,
    immutable,
    class_function,
    class_property,
    eq_test,
)

from haskpy import testing


# Some thoughts on design: One could implement all the methods (except match)
# in Maybe class by using the match method to choose the implementation. But
# this would be just clumsy and add overhead. Class inheritance is a Pythonic
# way of choosing the correct method implementation. Also, Just needs to
# support equality testing, so that's also easy to achieve by making it a
# class.


class Maybe(
        Monad,
        CommutativeMonoid,
        Hashable,
        Foldable,
        Eq,
):
    """Maybe type for optional values"""

    def match(self, *, Just, Nothing):
        raise NotImplementedError()

    @class_property
    def empty(cls):
        return Nothing

    @class_function
    def pure(cls, x):
        return Just(x)

    @class_function
    def sample_value(cls, a):
        return st.one_of(a.map(Just), st.just(Nothing))

    @class_function
    def sample_hashable_type(cls):
        t = testing.sample_hashable_type()
        return t.map(cls.sample_value)

    @class_function
    def sample_monoid_type(cls):
        t = testing.sample_monoid_type()
        return t.map(cls.sample_value)

    @class_function
    def sample_commutative_type(cls):
        t = testing.sample_commutative_type()
        return t.map(cls.sample_value)

    @class_function
    def sample_eq_type(cls):
        t = testing.sample_eq_type()
        return t.map(cls.sample_value)


class Just(Maybe):

    __x = attr.ib()

    def __init__(self, x):
        self.__x = x

    def match(self, *, Just, Nothing):
        return Just(self.__x)

    def map(self, f):
        return Just(f(self.__x))

    def apply_to(self, x):
        return x.map(self.__x)

    def bind(self, f):
        return f(self.__x)

    def append(self, m):
        return m.match(
            Nothing=lambda: self,
            Just=lambda x: Just(self.__x.append(x))
        )

    def fold_map(self, monoid, f):
        return f(self.__x)

    def foldl(self, combine, initial):
        return combine(initial, self.__x)

    def foldr(self, combine, initial):
        return combine(self.__x, initial)

    def length(self):
        return 1

    def to_iter(self):
        yield from (self.__x,)

    def __repr__(self):
        return "Just({0})".format(repr(self.__x))

    def __eq__(self, other):
        return other.match(
            Just=lambda x: self.__x == x,
            Nothing=lambda: False,
        )

    def __eq_test__(self, other, data):
        return other.match(
            Just=lambda x: eq_test(self.__x, x, data),
            Nothing=lambda: False,
        )


@singleton
@immutable
class Nothing(Maybe):

    def match(self, *, Just, Nothing):
        return Nothing()

    def map(self, f):
        return Nothing

    def apply_to(self, x):
        return Nothing

    def bind(self, f):
        return Nothing

    def append(self, m):
        return m

    def fold_map(self, monoid, f):
        return monoid.empty

    def foldl(self, combine, initial):
        return initial

    def foldr(self, combine, initial):
        return initial

    def length(self):
        return 0

    def to_iter(self):
        yield from ()

    def __repr__(self):
        return "Nothing"

    def __eq__(self, other):
        return other.match(Just=lambda _: False, Nothing=lambda: True)

    def __eq_test__(self, other, data):
        return other.match(Just=lambda _: False, Nothing=lambda: True)


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

    return MaybeM
