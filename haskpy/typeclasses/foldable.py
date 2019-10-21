import attr

from haskpy.utils import identity
from .typeclass import TypeclassMeta


@attr.s(frozen=True)
class Foldable(metaclass=TypeclassMeta):
    """Foldable typeclass

    Minimal complete definition:

    - ``fold_map`` or ``foldl`` or ``foldr``

    It is very strongly recommended to implement both ``foldl`` and ``foldr``
    because the default implementations won't scale up in Python.

    Note that ``foldl`` and ``foldr`` are sequential, but ``fold_map`` could be
    parallelized because it uses monoids. Thus, if parallelized implementation
    is needed, then also ``fold_map`` should be implemented.

    The default implementations are defined in circular fashion so that only
    one of ``fold_map``, ``foldl`` and ``foldr`` is strictly needed:
    ``fold_map`` uses ``foldl``, which uses ``foldr``, which uses ``fold_map``.
    But as said, instance implementations of at least both ``foldl`` and
    ``foldr`` are strongly recommended.

    """


    def fold_map(self, monoid, f):
        """Monoid m => t a -> (a -> m) -> m (ignoring ``monoid`` argument)

        The default implementation is based on ``foldl`` (or, if not
        implemented, recursively on ``foldr``). Thus, all possibilities for
        parallelism is lost.

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
        return self.foldl(
            lambda m, x: monoid.append(m, f(x)),
            monoid.empty,
        )


    def foldl(self, combine, initial):
        """t a -> (b -> a -> b) -> b -> b

        The default implementation is based on ``foldr`` (or, if not
        implemented, recursively on ``fold_map``). Either way, the default
        implementation doesn't scale up well, so an instance implementation is
        strongly recommended.

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
        #

        # (b -> a -> b) -> (a -> (b -> b))
        #
        # initial
        from haskpy.functions import compose
        return self.foldr(
            lambda a, f: compose(f, lambda b: combine(b, a)),
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

        """
        from haskpy.functions import Function
        return self.fold_map(
            Function,
            lambda a: lambda b: combine(a, b),
        )(initial)


    def fold(self, monoid):
        return self.fold_map(monoid, identity)


# @function
# def fold(monoid, xs):
#     pass


# @function
# def fold_map(monoid, f, xs):
#     pass
