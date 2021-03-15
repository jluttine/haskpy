"""Linked list of values

.. autosummary::
   :toctree:

   LinkedList
   Cons
   Nil
   iterate
   repeat
   replicate

"""

import attr
import functools
from hypothesis import strategies as st

from haskpy.typeclasses import Monad, Monoid, Foldable, Eq
from haskpy.types.either import Left, Right
from haskpy import testing
from haskpy.internal import (
    immutable,
    class_property,
    class_function,
)
from haskpy.testing import eq_test
from haskpy.types.function import function


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

    @class_property
    def empty(cls):
        return Nil

    @class_function
    def pure(cls, x):
        """a -> LinkedList a"""
        return Cons(x, lambda: Nil)

    def map(self, f):
        """List a -> (a -> b) -> List b"""
        return self.match(
            Nil=lambda: Nil,
            Cons=lambda x, xs: Cons(f(x), lambda: xs().map(f)),
        )

    def bind(self, f):
        """List a -> (a -> List b) -> List b"""

        def append_lazy(xs, lys):
            """LinkedList a -> (() -> LinkedList a) -> LinkedList a

            Append two linked lists. This function is "lazy" in its second
            argument, that is, ``lys`` is a lambda function that returns the
            linked list.

            """
            return xs.match(
                Nil=lambda: lys(),
                Cons=lambda x, lxs: Cons(x, lambda: append_lazy(lxs(), lys))
            )

        return self.match(
            Nil=lambda: Nil,
            Cons=lambda x, lxs: append_lazy(f(x), lambda: lxs().bind(f)),
        )

    def append(self, ys):
        """LinkedList a -> LinkedList a -> LinkedList a"""
        return self.match(
            Nil=lambda: ys,
            Cons=lambda x, lxs: Cons(x, lambda: lxs().append(ys))
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

    def __eq__(self, other):
        """LinkedList a -> LinkedList a -> bool"""
        # Here's a nice recursive solution:
        #
        # return self.match(
        #     Nil=lambda: other.match(
        #         Nil=lambda: True,
        #         Cons=lambda _, __: False,
        #     ),
        #     Cons=lambda x, xs: other.match(
        #         Nil=lambda: False,
        #         Cons=lambda y, ys: (x == y) and (xs() == ys()),
        #     ),
        # )
        #
        # However, it doesn't work because of Python has bad recursion support.
        # So, let's use recurse_tco which converts recursion to a loop:
        return self.recurse_tco(
            lambda acc, x: (
                acc.match(
                    # self is longer than other
                    Nil=lambda: Left(False),
                    Cons=lambda y, lys: (
                        # Elements don't match
                        Left(False) if x != y else
                        # All good thus far, continue
                        Right(lys())
                    )
                )
            ),
            lambda acc: acc.match(
                # Both lists are empty (or end at the same time)
                Nil=lambda: True,
                # other is longer than self
                Cons=lambda _, __: False,
            ),
            other,
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

    def recurse_tco(self, f, g, acc):
        """Recursion with tail-call optimization

        Type signature:

        ``LinkedList a -> (b -> a -> Either c b) -> (b -> c) -> b -> c``

        where ``a`` is the type of the elements in the linked list, ``b`` is
        the type of the accumulated value and ``c`` is the type of the result.
        Quite often, the accumulated value is also the end result, so ``b`` is
        ``c`` and ``g`` is an identity function.

        As Python supports recursion very badly, some typical recursion
        patterns are implemented as methods that convert specific recursions to
        efficients loops. This method implements the following pattern:

        .. code-block:: python

            >>> return self.match(
            ...     Nil=lambda: g(acc),
            ...     Cons=lambda x, lxs: f(acc, x).match(
            ...         Left=lambda y: y,
            ...         Right=lambda y: lxs().recurse_tco(f, g, y)
            ...     )
            ... )

        This recursion method supports short-circuiting and simple tail-call
        optimization. A value inside ``Left`` stops the recursion and returns
        the value. A value inside ``Right`` continues the recursion with the
        updated accumulated value.

        Examples
        --------

        For instance, the following recursion calculates the sum of the list
        elements until the sum exceeds one million:

        .. code-block:: python

            >>> from haskpy import Left, Right, iterate
            >>> xs = iterate(lambda x: x + 1, 1)
            >>> my_sum = lambda xs, acc: xs.match(
            ...     Nil=lambda: acc,
            ...     Cons=lambda y, ys: acc if acc > 1000000 else my_sum(xs, acc + y)
            ... )
            >>> my_sum(xs, 0)

        Unfortunately, this recursion exceeds Python maximum recursion depth
        because 1000000 is a large enough number. Note that this cannot be
        implemented with ``foldl`` because it doesn't support short-circuiting.
        Also, ``foldr`` doesn't work because it's right-associative so it
        cannot short-circuit based on the accumulator. But it can be calculated
        with this ``recurse_tco`` method which converts the recursion into a
        loop internally:

        .. code-block:: python

            >>> xs.recurse_tco(
            ...     lambda acc, x: Left(acc) if acc > 1000000 else Right(acc + x),
            ...     lambda acc: acc,
            ...     0
            ... )

        See also
        --------

        foldl
        foldr
        foldr_lazy

        """
        stop = False
        xs = self
        while not stop:
            (stop, acc, xs) = xs.match(
                Nil=lambda: (True, g(acc), Nil),
                Cons=lambda y, lys: f(acc, y).match(
                    Left=lambda z: (True, z, Nil),
                    Right=lambda z: (False, z, lys())
                )
            )
        return acc

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
        return functools.reduce(lambda a, b: combine(a)(b), self, initial)

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
            Cons=lambda x, xs: combine(x)(xs().foldr(combine, initial))
        )

    def foldr_lazy(self, combine, initial):
        r"""Foldable t => t a -> (a -> (() -> b) -> (() -> b)) -> b -> b

        Nonstrict right-associative fold with support for lazy recursion,
        short-circuiting and tail-call optimization.

        HOW ABOUT [a,b,c,d,e,f,g,h,...] -> (a(b(c(d(e))))) UNTIL TOTAL STRING
        LENGTH IS X?

        Parameters
        ----------

        combine : curried function

        See also
        --------

        haskpy.typeclasses.foldable.foldr_lazy

        """

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

    #
    # Sampling methods for property tests
    #

    # @class_function
    # @st.composite
    # def sample_value(draw, cls, a):
    #     return draw(
    #         st.one_of(
    #             st.just(Nil),
    #             a.map(
    #                 lambda x: Cons(
    #                     x,
    #                     lambda: draw(cls.sample_value(a))
    #                 )
    #             )
    #         )
    #     )
    #     #return st.lists(a, max_size=10).map(lambda xs: cls(*xs))

    @class_function
    def sample_value(cls, a, max_depth=3):
        # It's not possible to sample linked lists lazily because hypothesis
        # doesn't support that sampling happens at some later point (the
        # sampler gets "frozen"). So, we must sample everything at once,
        # although we then add the "lazy" lambda wrapping to the pre-sampled
        # values.
        #
        # This non-lazy sampling could be implemented recursively as follows:
        #
        return (
            st.just(Nil) if max_depth <= 0 else
            st.deferred(
                lambda: st.one_of(
                    st.just(Nil),
                    a.flatmap(
                        lambda x: cls.sample_value(a, max_depth=max_depth-1).map(
                            lambda xs: Cons(x, lambda: xs)
                        )
                    )
                )
            )
        )
        #
        # However, this can cause RecursionError in Python, so let's write it
        # as a loop instead:

    sample_type = testing.create_type_sampler(
        testing.sample_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler()
    sample_apply_type_constructor = sample_functor_type_constructor
    sample_applicative_type_constructor = sample_functor_type_constructor
    sample_monad_type_constructor = sample_functor_type_constructor

    sample_semigroup_type = testing.create_type_sampler(
        testing.sample_type(),
    )
    sample_monoid_type = sample_semigroup_type

    sample_eq_type = testing.create_type_sampler(
        testing.sample_eq_type(),
    )

    def __eq_test__(self, other, data=None):
        return self.match(
            Nil=lambda: other.match(
                Nil=lambda: True,
                Cons=lambda _, __: False,
            ),
            Cons=lambda x, lxs: other.match(
                Nil=lambda: False,
                Cons=lambda y, lys: (
                    eq_test(x, y, data) and
                    eq_test(lxs(), lys(), data)
                ),
            ),
        )

    sample_foldable_type_constructor = testing.create_type_constructor_sampler()
    sample_foldable_functor_type_constructor = sample_foldable_type_constructor


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
