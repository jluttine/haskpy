import attr

from .functor import Functor
from haskpy.utils import function


@attr.s(frozen=True)
class Applicative(Functor):
    """Must define at least pure and either apply or apply_to

    Functor methods are given defaults based on Applicative methods.

    """


    @classmethod
    def pure(cls, x):
        raise NotImplementedError()


    @function
    def apply(self, f):
        return f.apply_to(self)


    @function
    def apply_to(self, x):
        return x.apply(self)


    @function
    def map(self, f):
        # Default implementation for Functor based on Applicative
        return self.pure(f).apply_to(self)


@function
def liftA2(f, x, y):
    return x.map(f).apply(y)


@function
def apply(f, x):
    return x.apply(f)
