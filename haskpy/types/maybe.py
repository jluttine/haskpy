"""Optional values

Types:

.. autosummary::
   :toctree:

    Maybe

Data constructors:

.. autosummary::
   :toctree:

    Nothing
    Just

Monad transformers:

.. autosummary::
   :toctree:

    MaybeT

"""

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
from haskpy.internal import (
    immutable,
    class_function,
    class_property,
)
from haskpy.testing import eq_test
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
    """Type ``Maybe a`` for a value that might be present or not

    :py:class:`.Maybe` monad is one of the simplest yet very useful monads. It
    represents a case when you might have a value or not. If you have a value,
    it's wrapped with :py:func:`.Just`:

    .. code-block:: python

    >>> x = hp.Just(42)
    >>> x
    Just(42)
    >>> type(x)
    Maybe

    If you don't have a value, it's represented with :py:data:`.Nothing`:

    .. code-block:: python

    >>> y = hp.Nothing
    >>> y
    Nothing
    >>> type(y)
    Maybe

    Quite often Python programmers handle this case by using ``None`` to
    represent "no value" and then just the plain value otherwise. However,
    whenever you want to do something with the value, you need to first check
    if it's ``None`` or not, and handle both cases somehow. And, more
    importantly, you need to remember to do this every time you use a value
    that might be ``None``.

    With HaskPy, it is explicit that the value might exist or not, so you are
    forced to handle both cases. Or, more interestingly, you can just focus on
    the value and let HaskPy take care of the special case. Let's see what this
    means. Say you have a function that you'd like to apply to the value:

    .. code-block:: python

    >>> f = lambda v: v + 1

    You can use :py:meth:`.Functor.map` method to apply it to the value:

    .. code-block:: python

    >>> x.map(f)
    Just(43)

    Or, equivalently, use a function:

    .. code-block:: python

    >>> hp.map(f, x)
    Just(43)

    Quite often there are corresponding functions for the methods and it may
    depend on the context which one is more convenient to use. The order of the
    arguments might be slightly different in the function than in the method
    though.

    But what would've happened if we had ``Nothing`` instead?

    .. code-block:: python

    >>> hp.map(f, y)
    Nothing

    So, nothing was done to ``Nothing``. But the important thing is that you
    didn't need to worry about whether ``x`` or ``y`` was ``Nothing`` or
    contained a real value, :py:class:`Maybe` took care of that under the hood.
    If in some cases you need to handle both cases explicitly, you can use
    :py:func:`.match` function:

    .. code-block:: python

    >>> g = hp.match(Just=lambda v: 2*v, Nothing=lambda: 666)
    >>> g(x)
    84
    >>> g(y)
    666

    With :py:func:`.match` you need to explicitly handle all possible cases or
    you will get an error even if your variable wasn't ``Nothing``. Therefore,
    you'll never forget to take into account ``Nothing`` case as might happen
    with the classic ``None`` approach.

    Alright, this was just a very tiny starter about :py:class:`.Maybe`.

    See also
    --------

    haskpy.types.either.Either

    """

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
"""Nada"""


def Just(x):
    """Just do it"""
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
