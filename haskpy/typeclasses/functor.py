import attr

from haskpy.utils import function


@attr.s(frozen=True)
class Functor():
    """Covariant functor"""


    @function
    def map(self, f):
        """Haskell fmap"""
        raise NotImplementedError()


    @function
    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)


@function
def map(f, x):
    return x.map(f)


@function
def replace(a, x):
    return x.replace(a)
