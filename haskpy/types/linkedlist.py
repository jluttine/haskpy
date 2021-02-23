import attr
import functools
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid, Foldable, Eq
from haskpy import testing
from haskpy.utils import (
    immutable,
    class_property,
    class_function,
    eq_test,
    curry,
)
from haskpy.functions import function


@immutable()
class LinkedList(Monad, Monoid, Foldable, Eq):
    """Linked-list with "lazy" Cons

    The "lazy" Cons makes it possible to construct infinite lists. For
    instance, an infinite list of a repeated value 42 can be constructed as:

    .. code-block:: python

        >>> repeat(42)
        Cons(42, Cons(42, Cons(42, Cons(42, Cons(42, Cons(42, ...))))))

    You can use, for instance, ``scanl`` and ``map`` to create more complex
    infinite lists from a simple one:

    .. code-block:: python

        >>> xs = repeat(1).scanl(lambda acc, x: acc + x)
        >>> xs
        Cons(1, Cons(2, Cons(3, Cons(4, Cons(5, Cons(6, ...))))))
        >>> xs.map(lambda x: x ** 2)
        Cons(1, Cons(4, Cons(9, Cons(16, Cons(25, Cons(36, ...))))))

    Note that this works also for very long lists:

    .. code-block:: python

        >>> xs.drop(10000)
        Cons(10001, Cons(10002, Cons(10003, Cons(10004, Cons(10005, Cons(10006, ...))))))

    One can create infinite lists by using a recursive definition:

    .. code-block:: python

        >>> xs = Cons(42, lambda: xs)

    But beware that this kind of recursive definition doesn't always work as
    one might expect. For instance, the following construction causes huge
    recursion depths:

    .. code-block:: python

        >>> xs = Cons(1, lambda: xs.map(lambda y: y + 1))
        >>> xs
        Cons(1, Cons(2, Cons(3, Cons(4, Cons(5, Nil)))))
        >>> xs.drop(10000)
        RecursionError: maximum recursion depth exceeded while calling a Python object

    This happens because each value depends recursively on all the previous
    values

    """

    match = attr.ib()

    def map(self, f):
        """List a -> (a -> b) -> List b"""
        return self.match(
            Nil=lambda: Nil,
            Cons=lambda x, xs: Cons(f(x), lambda: xs().map(f)),
        )

    def take(self, n):
        # Note that here we can use a recursive definition because the
        # recursion stops at lambda, so the list is consumed lazily.
        return self.match(
            Nil=lambda: Nil,
            Cons=lambda x, xs: (
                Nil if n <= 0 else
                Cons(x, lambda: xs().take(n-1))
            ),
        )

    def drop(self, n):
        # This is the trivial recursive implementation:
        #
        # return self.match(
        #     Nil=lambda: Nil,
        #     Cons=lambda x, xs: (
        #         Cons(x, xs) if n <= 0 else
        #         xs().drop(n-1)
        #     ),
        # )
        #
        # However, recursion causes stack overflow for long lists with large n.
        # So, let's use a loop:
        xs = self
        for i in range(n):
            (exit, xs) = xs.match(
                Nil=lambda: (True, Nil),
                Cons=lambda z, zs: (False, zs())
            )
            if exit:
                break
        return xs

    @class_function
    def pure(cls, x):
        """a -> LinkedList a"""
        return Cons(x, Nil)

    def __eq__(self, other):
        """LinkedList a -> LinkedList a -> bool"""
        return self.match(
            Nil=lambda: other.match(
                Nil=lambda: True,
                Cons=lambda _, __: False,
            ),
            Cons=lambda x, xs: other.match(
                Nil=lambda: False,
                Cons=lambda y, ys: (x == y) and (xs() == ys()),
            ),
        )

    def to_iter(self):
        lxs = lambda: self
        while True:
            (stop, x, lxs) = lxs().match(
                Nil=lambda: (True, None, None),
                Cons=lambda z, lzs: (False, z, lzs),
            )
            if stop:
                break
            yield x

    def foldl(self, combine, initial):
        """Foldable t => t a -> (b -> a -> b) -> b -> b

        Strict left-associative fold

        ((((a + b) + c) + d) + e)

        """
        # NOTE: The following simple recursive implementation doesn't work
        # because it can exceed Python maximum recursion depth:
        #
        # return self.match(
        #     Nil=lambda: initial,
        #     Cons=lambda x, xs: xs().foldl(combine, combine(initial, x)),
        # )
        #
        # So, let's use a for-loop based solution instead:
        return functools.reduce(combine, self, initial)

    def foldr(self, combine, initial):
        """Foldable t => t a -> (a -> b -> b) -> b -> b

        Strict right-associative fold. Note that this doesn't work for infinite
        lists because it's strict. You probably want to use ``foldr_lazy`` or
        ``foldl`` instead as this function easily exceeds Python maximum
        recursion depth (or the stack overflows).

        ..code-block:: python

            >>> xs = iterate(lambda x: x + 1, 1)
            >>> xs.foldr(lambda y, ys: Cons(2 * y, lambda: ys), Nil)
            RecursionError: maximum recursion depth exceeded while calling a Python object

        """
        return self.match(
            Nil=lambda: initial,
            Cons=lambda x, xs: combine(x, xs().foldr(combine, initial))
        )

    def foldr_lazy(self, combine, initial):
        r"""Foldable t => t a -> (a -> (() -> b) -> (() -> b)) -> b -> b

        Nonstrict right-associative fold with support for lazy recursion,
        short-circuiting and tail-call optimization.

        See also
        --------

        haskpy.foldr_lazy

        """

        combine = curry(combine)

        def step(x, lxs):
            """A single recursion step

            Utilizes tail-call optimization if used.

            """
            lacc_prev = lambda: run(lxs())
            lacc_next = combine(x)(lacc_prev)

            # Special case: Tail call optimization! If the lazy accumulator
            # stays unmodified, we can just iterate as long as it's not
            # modified.
            while lacc_next is lacc_prev:
                (lxs, lacc_next) = lxs().match(
                    Nil=lambda: (Nil, lambda: initial),
                    Cons=lambda z, lzs: (lzs, combine(z)(lacc_next)),
                )

            # Just return and let the normal recursion roll
            return lacc_next()

        def run(xs):
            """Run the recursion

            This wouldn't need to be wrapped in a separate function as we could
            call foldr_lazy recursively. However, as we explicitly curry
            combine-function, let's avoid doing that at every step.

            """
            return xs.match(
                Nil=lambda: initial,
                Cons=step,
            )

        return run(self)

    def scanl(self, f):
        return self.match(
            Nil=lambda: Nil,
            Cons=lambda x, xs: Cons(x, lambda: xs()._scanl(f, x)),
        )

    def _scanl(self, f, acc):
        def create_cons(x, xs):
            z = f(acc, x)
            return Cons(z, lambda: xs()._scanl(f, z))
        return self.match(
            Nil=lambda: Nil,
            Cons=create_cons,
        )

    def __repr__(self):
        return self.__repr()

    def __repr(self, maxdepth=5):
        return self.match(
            Nil=lambda: "Nil",
            Cons=lambda x, xs: "Cons({0}, {1})".format(
                repr(x),
                "..." if maxdepth <= 0 else xs().__repr(maxdepth-1),
            ),
        )


Nil = LinkedList(match=lambda Nil, Cons: Nil())


def Cons(x, xs):
    """xs is a lambda function"""
    return LinkedList(match=lambda Nil, Cons: Cons(x, xs))


@function
def iterate(f, x):
    return Cons(x, lambda: iterate(f, f(x)))


@function
def repeat(x):
    xs = Cons(x, lambda: xs)
    return xs


@function
def replicate(n, x):
    return (
        Nil if n <= 0 else
        Cons(x, lambda: replicate(n - 1, x))
    )
