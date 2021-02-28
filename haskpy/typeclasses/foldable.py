import itertools
from warnings import warn, filterwarnings, catch_warnings
import hypothesis.strategies as st
from hypothesis import given

from haskpy.utils import (
    identity,
    PerformanceWarning,
    assert_output,
    class_function,
    abstract_class_function,
)
from haskpy import testing
from .typeclass import Type


class Foldable(Type):
    """Foldable typeclass

    Strictly minimal complete definition:

    - ``fold_map`` or ``foldl`` or ``foldr``

    Recommended minimal complete definition:

    - ``foldl``

    - ``foldr``

    - ``to_iter``

    - ``length``

    If default implementation is used for any of those, a performance warning
    is raised.

    It is very strongly recommended to implement both ``foldl`` and ``foldr``
    because the default implementations won't scale up in Python. Also,
    ``to_iter`` is strongly recommended as many other methods rely on that and
    the default implementation is slow.

    Note that ``foldl`` and ``foldr`` are sequential, but ``fold_map`` could be
    parallelized because it uses monoids. Thus, if parallelized implementation
    is needed, then also ``fold_map`` should be implemented.

    The default implementations are defined in circular fashion so that only
    one of ``fold_map``, ``foldl`` and ``foldr`` is strictly needed:
    ``fold_map`` uses ``foldl``, which uses ``foldr``, which uses ``fold_map``.
    But as said, instance implementations of at least both ``foldl`` and
    ``foldr`` are strongly recommended.

    Examples
    --------

    In Haskell, Data.Set is Foldable, but not a Functor

    """

    def fold_map(self, monoid, f):
        """Monoid m => t a -> (a -> m) -> m (ignoring ``monoid`` argument)

        The default implementation is based on ``foldl`` (or, if not
        implemented, recursively on ``foldr``). Thus, all possibilities for
        parallelism is lost.

        ``monoid`` is the monoidic class of the values inside the foldable. It
        is only used to determine the identity value.

        """
        # In principle, we could just deduce the monoid class from the values
        # inside the container. But that doesn't work when the container is
        # empty (although it works in Haskell because of the smart type
        # system). Thus, we need to pass the monoid class explicitly. It's more
        # consistent to require it always than just when the container is
        # empty. If we had guaranteed non-empty containers, then the class
        # could be inferred from the values inside.
        #
        # NOTE: foldl and foldr are sequential because they cannot assume
        # initial is empty. But fold_map can be parallelized. Thus, we cannot
        # use foldl nor foldr here.

        # NOTE: fold_map should also work for infinite lists! This works in
        # Haskell:
        #
        # foldMap id (repeat (Any True))

        # FIXME: THIS DEFAULT IMPLEMENTATION ISN'T CORRECT BECAUSE IT DOESN'T
        # WORK ON INFINITE LISTS. IN HASKELL:
        #
        # myfoldr combine initial xs = (foldl (\f -> \a -> (f . (\b -> combine a b))) id xs) initial
        #
        # myfoldr const 2 [0..]
        return self.foldl(
            lambda m: lambda x: m.append(f(x)),
            monoid.empty,
        )

    def foldl(self, combine, initial):
        """t a -> (b -> a -> b) -> b -> b

        The default implementation is based on ``foldr`` (or, if not
        implemented, recursively on ``fold_map``). Either way, the default
        implementation doesn't scale up well, so an instance implementation is
        strongly recommended.

        Intuition:

        - equivalent to for-loop on lists

        - never works on infinite lists (so not possible to implement ``map``
          in terms of ``foldl``)

        References
        ----------

        `Tony Morris - An Intuition for List Folds
        <https://www.youtube.com/watch?v=GPwtT31zKRY>`_

        """
        # NOTE: An intuitive trivial implementation would be as follows, but
        # that is incorrect:
        #
        #   return self.foldr(lambda a, b: combine(b, a), initial)
        #
        # It's wrong because it results in reversed order for the values in the
        # container:
        #
        # >>> List("a", "b", "c").foldl(lambda a, b: "({0}+{1})".format(a, b), "x")
        # '(((x+c)+b)+a)'
        #
        # The correct answer is:
        #
        # '(((x+a)+b)+c)'
        from haskpy.functions import compose
        warn("Using default implementation of foldl", PerformanceWarning)
        return self.foldr(
            lambda a: lambda f: compose(f, lambda b: combine(b)(a)),
            identity,
        )(initial)

    def foldr(self, combine, initial):
        """t a -> (a -> b -> b) -> b -> b

        .. warning::

            The default is very poor in Python. It is strongly recommended to
            provide an instance implementation for this.

        The default implementation uses ``fold_map`` by utilizing
        (endo)function monoid:

          empty :: b -> b

          append :: (b -> b) -> (b -> b) -> (b -> b)

        One can see ``combine`` function as a transformation to this monoid:

          combine :: a -> (b -> b)

        Then, just use endofunction monoid to compose all those ``b -> b``
        endofunctions into a single endofunction ``b -> b``. Finally, apply
        this function to the initial value.

        Intuition:

        - performs constructor replacement

        - may work on infinite lists

        - doesn't "calculate from the right" but associates to the right
          (otherwise it couldn't work on infinite lists)

        References
        ----------

        `Tony Morris - An Intuition for List Folds
        <https://www.youtube.com/watch?v=GPwtT31zKRY>`_

        """
        from haskpy.types.monoids import Endo
        warn("Using default implementation of foldr", PerformanceWarning)
        return self.fold_map(
            Endo,
            lambda x: Endo(lambda y: combine(x)(y)),
        ).app_endo(initial)

    def fold(self, monoid):
        return self.fold_map(monoid, identity)

    def fold2(self, monoid):
        return self.fold_map(monoid, identity)

    def to_iter(self):
        """t a -> Iter a

        Instead of to_list (as in Haskell), let's provide to_iter. With
        iterables, we can write efficient implementations for many other
        methods (e.g., sum, elem) even for large or sometimes infinite
        foldables.

        The default implementation isn't very efficient as it uses folding to
        construct the iterator.

        """
        warn("Using default implementation of to_iter", PerformanceWarning)
        return self.foldl(
            lambda acc, x: itertools.chain(acc, (x,)),
            itertools.chain()
        )

    def head(self, default):
        """Return head (or default if no head): ``f a -> a -> a``"""
        # FIXME? Or flip const?
        return self.foldr(const, default)

    def length(self):
        """t a -> int

        The default implementation isn't very efficient as it traverses through
        the iterator.

        """
        warn("Using default implementation of length", PerformanceWarning)
        return sum(1 for _ in self.to_iter())

    def sum(self):
        """t a -> number"""
        return sum(self.to_iter())

    def null(self):
        """t a -> bool"""
        return all(False for _ in self.to_iter())

    def elem(self, x):
        """t a -> a -> bool"""
        return any(x == y for y in self.to_iter())

    def __iter__(self):
        """Override to_iter if you want to change the default implementation"""
        yield from self.to_iter()

    def __len__(self):
        """Override length if you want to change the default implementation"""
        return self.length()

    def __contains__(self, x):
        """Override elem if you want to change the default implementation"""
        return self.elem(x)

    # TODO:
    #
    # - maximum
    # - minimum
    # - product
    # - to_list

    #
    # Sampling methods for property tests
    #

    @abstract_class_function
    def sample_foldable_type(cls, elements):
        pass

    @abstract_class_function
    def sample_foldable_functor_type(cls, elements):
        """Needed only for subclasses of both Foldable and Functor"""
        pass

    #
    # Test Foldable laws
    #

    @class_function
    @assert_output
    def assert_foldable_fold_map(cls, xs, monoid, f):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import fold_map
        return (
            Foldable.fold_map(xs, monoid, f),
            xs.fold_map(monoid, f),
            fold_map(monoid, f, xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_fold_map(cls, data):
        # Draw types
        from haskpy.typeclasses import Monoid
        monoid = data.draw(testing.sample_class(Monoid))
        a = data.draw(testing.sample_eq_type())
        b = data.draw(monoid.sample_monoid_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        f = data.draw(testing.sample_function(b))
        xs = data.draw(fa)

        cls.assert_foldable_fold_map(xs, monoid, f, data=data)
        return

    @class_function
    @assert_output
    def assert_foldable_foldr(cls, xs, combine, initial):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import foldr
        return (
            Foldable.foldr(xs, combine, initial),
            xs.foldr(combine, initial),
            foldr(combine, initial, xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_foldr(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        xs = data.draw(fa)
        g = data.draw(testing.sample_function(testing.sample_function(b)))
        initial = data.draw(b)

        with catch_warnings():
            filterwarnings("ignore", category=PerformanceWarning)
            cls.assert_foldable_foldr(xs, g, initial, data=data)

        return

    @class_function
    @assert_output
    def assert_foldable_foldl(cls, xs, combine, initial):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import foldl
        return (
            Foldable.foldl(xs, combine, initial),
            xs.foldl(combine, initial),
            foldl(combine, initial, xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_foldl(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        b = data.draw(testing.sample_eq_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        xs = data.draw(fa)
        initial = data.draw(b)
        g = data.draw(testing.sample_function(testing.sample_function(b)))

        with catch_warnings():
            filterwarnings("ignore", category=PerformanceWarning)
            cls.assert_foldable_foldl(xs, g, initial, data=data)

        return

    @class_function
    @assert_output
    def assert_foldable_fold(cls, xs, monoid):
        from haskpy.functions import fold
        # The default implementation defines the law (with respect to other
        # methods)
        return (
            Foldable.fold(xs, monoid),
            xs.fold(monoid),
            fold(monoid, xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_fold(cls, data):
        # Draw types
        from haskpy.typeclasses import Monoid
        monoid = data.draw(testing.sample_class(Monoid))
        a = data.draw(monoid.sample_monoid_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        xs = data.draw(fa)

        cls.assert_foldable_fold(xs, monoid, data=data)
        return

    @class_function
    @assert_output
    def assert_foldable_length(cls, xs):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import length
        return (
            Foldable.length(xs),
            len(xs),
            length(xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_length(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        xs = data.draw(fa)

        with catch_warnings():
            filterwarnings("ignore", category=PerformanceWarning)
            cls.assert_foldable_length(xs, data=data)

        return

    @class_function
    @assert_output
    def assert_foldable_null(cls, xs):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import null
        return (
            Foldable.null(xs),
            xs.null(),
            null(xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_null(cls, data):
        # Draw types
        a = data.draw(testing.sample_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        xs = data.draw(fa)

        with catch_warnings():
            filterwarnings("ignore", category=PerformanceWarning)
            cls.assert_foldable_null(xs, data=data)

        return

    @class_function
    @assert_output
    def assert_foldable_sum(cls, xs):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import sum
        return (
            Foldable.sum(xs),
            xs.sum(),
            sum(xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_sum(cls, data):
        # Draw types
        fa = data.draw(cls.sample_foldable_type(st.integers()))

        # Draw values
        xs = data.draw(fa)

        with catch_warnings():
            filterwarnings("ignore", category=PerformanceWarning)
            cls.assert_foldable_sum(xs, data=data)

        return

    @class_function
    @assert_output
    def assert_foldable_elem(cls, xs, e):
        # The default implementation defines the law (with respect to other
        # methods)
        from haskpy.functions import elem
        return (
            Foldable.elem(xs, e),
            e in xs,
            elem(e, xs),
        )

    @class_function
    @given(st.data())
    def test_foldable_elem(cls, data):
        # Draw types
        a = data.draw(testing.sample_eq_type())
        fa = data.draw(cls.sample_foldable_type(a))

        # Draw values
        e = data.draw(a)
        xs = data.draw(fa)

        with catch_warnings():
            filterwarnings("ignore", category=PerformanceWarning)
            cls.assert_foldable_elem(xs, e, data=data)

        return

    @class_function
    @assert_output
    def assert_foldable_functor(cls, xs, monoid, f):
        # Functor and foldable instances should be consistent
        return (
            xs.fold_map(monoid, f),
            xs.map(f).fold(monoid),
        )

    @class_function
    @given(st.data())
    def test_foldable_functor(cls, data):

        from .functor import Functor
        import pytest
        if not issubclass(cls, Functor):
            pytest.skip("{0} not Functor".format(cls.__name__))

        # Draw types
        from haskpy.typeclasses import Monoid
        monoid = data.draw(testing.sample_class(Monoid))
        b = data.draw(monoid.sample_monoid_type())
        a = data.draw(testing.sample_eq_type())
        fa = data.draw(cls.sample_foldable_functor_type(a))

        # Draw values
        f = data.draw(testing.sample_function(b))
        xs = data.draw(fa)

        cls.assert_foldable_functor(xs, monoid, f, data=data)
        return


# Foldable-related functions are defined in function module because of circular
# dependency.
