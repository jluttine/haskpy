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
    Eq,
    Traversable,
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
        Traversable,
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

    def sequence(self, applicative):
        return self.match(
            Nothing=lambda: applicative.pure(Nothing),
            # Instead of x.map(Just), access the method via the class so that
            # if the given applicative class is inconsistent with the contained
            # value an error would be raised. This helps making sure that if
            # sequence works for case Just, it'll be consistent with case
            # Nothing. "If it runs, it probably works."
            Just=lambda x: applicative.map(x, Just),
        )

    def __repr__(self):
        return self.match(
            Nothing=lambda: "Nothing",
            Just=lambda x: "Just({0})".format(repr(x)),
        )

    def __hash__(self):
        return self.match(
            # Use some random strings in hashing
            Nothing=lambda: hash("hfauwovnohuwehrofasdlnvlspwfoij"),
            Just=lambda x: hash(("fwaoivaoiejfaowiefijafsduhasdo", x))
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

    sample_type = testing.create_type_sampler(
        testing.sample_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler()
    sample_foldable_type_constructor = testing.create_type_constructor_sampler()

    # Some typeclass instances have constraints for the type inside Maybe

    sample_hashable_type = testing.create_type_sampler(
        testing.sample_hashable_type(),
    )

    sample_semigroup_type = testing.create_type_sampler(
        testing.sample_semigroup_type(),
    )

    sample_commutative_type = testing.create_type_sampler(
        testing.sample_commutative_type(),
    )

    sample_eq_type = testing.create_type_sampler(
        testing.sample_eq_type(),
    )


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

    is_eq = issubclass(M, Eq)

    bases = [] + (
        [Eq] if is_eq else []
    )

    @immutable
    class MaybeM(Monad, *bases, metaclass=MetaMaybeM):

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
        def sample_type(cls):
            return M.sample_monad_type_constructor().map(
                lambda m: m(Maybe.sample_type()).map(cls)
            )

        if is_eq:
            @class_function
            def sample_eq_type(cls):
                return M.sample_monad_type_constructor().map(
                    # Note that we can't be really sure if the Eq instance of M
                    # has any constraints for the contained type (i.e., Maybe
                    # in this case). A simple pathological monad M could be
                    # such that it totally ignores the contained type. However,
                    # it's the most typical case that M requires the contained
                    # type to be an instance of Eq too, so let's assume so.
                    # There's no real harm as this is only sampling for tests
                    # so it means we just use a bit more limited set of
                    # samples. But in practice, this is almost always needed.
                    lambda m: m(Maybe.sample_eq_type()).map(cls)
                )

        @class_function
        def sample_functor_type_constructor(cls):
            # This is a Monad transformer class, so let's sample monads even
            # when functors are required.
            return Maybe.sample_monad_type_constructor().flatmap(
                lambda f: M.sample_monad_type_constructor().map(
                    lambda g: lambda a: g(f(a)).map(cls)
                )
            )

    return MaybeM
