import attr
import toolz

from haskpy.function import Function


@attr.s(frozen=True)
class Functor():
    """Covariant functor"""


    @Function
    def map(self, f):
        """Haskell fmap"""
        raise NotImplementedError()


    @Function
    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)


@Function
@toolz.curry
def map(f, x):
    return x.map(f)


@Function
def replace(a, x):
    return x.replace(a)
