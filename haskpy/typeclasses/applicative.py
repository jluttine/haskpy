import attr

from .functor import Functor
from haskpy.utils import function


@attr.s(frozen=True)
class Applicative(Functor):
    """Must define at least pure and either apply or apply_to

    The required Functor methods are given defaults based on the required
    Applicative methods.

    """


    @classmethod
    def pure(cls, x):
        """a -> m a"""
        raise NotImplementedError()


    @function
    def apply(self, f):
        """m a -> m (a -> b) -> m b

        Default implementation is based on ``apply_to``.

        """
        return f.apply_to(self)


    @function
    def apply_to(self, x):
        """f (a -> b) -> f a -> f b

        Default implementation is based on ``apply``.

        """
        return x.apply(self)


    @function
    def map(self, f):
        """m a -> (a -> b) -> m b

        Default implementation is based on ``apply``:

        self :: m a

        f :: a -> b

        pure f :: m (a -> b)

        apply :: m a -> m (a -> b) -> m b

        """
        # Default implementation for Functor based on Applicative
        cls = type(self)
        mf = cls.pure(f)
        return self.apply(mf)


@function
def liftA2(f, x, y):
    return x.map(f).apply(y)


@function
def apply(f, x):
    return x.apply(f)
