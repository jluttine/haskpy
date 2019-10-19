import attr

from .functor import Functor


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


    def apply(self, f):
        """m a -> m (a -> b) -> m b

        Default implementation is based on ``apply_to``.

        """
        return f.apply_to(self)


    def apply_to(self, x):
        """f (a -> b) -> f a -> f b

        Default implementation is based on ``apply``.

        """
        return x.apply(self)


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


# Applicative-related functions are defined in function module because of
# circular dependency.
