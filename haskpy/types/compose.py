import attr
import functools

from haskpy.typeclasses import Applicative
from haskpy.functions import map, apply


def Compose(X, Y):
    """Compose two type constructors X and Y into a single type constructor

    Kind:

      Compose :: (* -> *) -> (* -> *) -> * -> *

    That is, it takes two type constructors and one concrete type to create a
    concrete type. Another way to see it is that it takes two one-argument type
    constructors and returns a one-argument type constructor:

      Compose :: (* -> *) -> (* -> *) -> (* -> *)

    That's how we can see it here.

    Two nested Applicative structures are merged into one layer:

      Composed :: f1 (f2 a) -> f f1 f2 a

    Note that ``f`` is a type constructor of three arguments as shown by its
    kind above.

    Some motivation for the current implementation:

    - Why not just a class that takes a value/object? Why do we need this
      function wrapper Compose that takes classes as arguments? Because we need
      to be able to implement the class method ``pure``. Also, this solution
      would make it possible to decide the parent classes based on the classes
      of X and Y, so that composed result isn't, for instance, Foldable unless
      both X and Y are Foldable.

    - Why the class Composed doesn't have ``__init__`` that passes ``*args``
      and ``**kwargs`` to the outer class constructor? It would make it
      slightly more convenient to create values, right? Not really. We want to
      be able to transform already existing non-composed values to composed
      values. For that we need to just take a value, not the outer class
      constructor arguments. Also, this allows us to decompose and compose in
      turns without problems. Also, it is more explicit for the user that which
      are the underlying types because they need to write those when creating
      values.

    So, in comparison to Haskell, the function ``Compose`` corresponds to
    type-level composing and ``Composed`` corresponds to value-level type
    converter. We need explicit type-level composing here because we need some
    class methods such as ``pure``.

    """


    class ComposedMeta(type(Applicative)):


        InnerClass = Y
        OuterClass = X


        def pure(cls, x):
            """a -> f a

            Without composition, this corresponds to:

              a -> f1 (f2 a)

            """
            return cls(X.pure(Y.pure(x)))


        def compress_init(cls):
            """Create a bit simplified constructor

            XY = Compose(X, Y)

            Instead of something like:

              xy = XY(X(Y(1), Y(2)))

            You can write use compressed constructor:

              XYc = XY.compress_init()

            And then create objects as:

              xy = XYc(Y(1), Y(2))

            Note that the constructor of X is now missing.

            """
            return functools.wraps(X)(
                lambda *args, **kwargs: cls(X(*args, **kwargs))
            )


        def __repr__(cls):
            return "Compose({0}, {1})".format(
                repr(cls.OuterClass),
                repr(cls.InnerClass),
            )


        def sample_value(cls, a):
            return X.sample_value(Y.sample_value(a)).map(cls)


    # It's also Foldable and Traversable if both X and Y are.


    @attr.s(frozen=True, repr=False)
    class Composed(Applicative, metaclass=ComposedMeta):


        # The attribute name may sound weird but it makes sense once you
        # understand that this indeed is the not-yet-composed variable and if
        # you want to decompose a composed variable you get it by x.decomposed.
        # Thus, there's no need to write a simple function to just return this
        # attribute, just use this directly.
        decomposed = attr.ib()


        def apply(self, f):
            """f a -> f (a -> b) -> f b

            Without composition, this corresponds to:

              f1 (f2 a) -> (f1 (f2 (a -> b))) -> f1 (f2 b)

              f1 a -> f1 (a -> b) -> f1 b

            """
            # TODO: Check this..
            #
            # NOTE: Instead of wrapping with Composed(...), use a bit more
            # verbose attr.evolve(self, ...) so that a correct class is used in
            # subclasses.
            return attr.evolve(
                self,
                decomposed=(apply(map(apply, f.decomposed), self.decomposed))
            )


        def map(self, f):
            """(a -> b) -> f a -> f b

            Without composition, this corresponds to:

              map . map :: (a -> b) -> f1 (f2 a) -> f1 (f2 b)

            """
            # This implementation isn't necessary because Applicative has a
            # default implementation. But let's just provide this simple
            # implementation for efficiency.
            #
            # NOTE: Instead of wrapping with Composed(...), use a bit more
            # verbose attr.evolve(self, ...) so that a correct class is used in
            # subclasses.
            return attr.evolve(
                self,
                decomposed=(map(map(f))(self.decomposed))
            )


        def decompose(self):
            return self.decomposed


        def __repr__(self):
            return "{0}({1})".format(
                repr(self.__class__),
                repr(self.decomposed),
            )


    return Composed


def decompose(x):
    return x.decomposed
