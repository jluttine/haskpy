import attr

from haskpy.typeclasses.applicative import Applicative
from haskpy.utils import singleton
from haskpy.function import Function


__all__ = ["Just", "Nothing"]


@attr.s(frozen=True, repr=False)
class Just(Applicative):


    value = attr.ib()


    @Function
    def map(self, f):
        # I suppose currying is capturing these type errors and messes up
        # everything. For instance, this doesn't raise an error:
        #
        # >>> import haskpy
        # >>> haskpy.Just(pyhask.List(1,2,3)).map(lambda x: x+1)
        #
        # Even raising explicit TypeError here doesn't break:
        #
        # raise TypeError()
        #
        # This seems.. just.. wrong.. from toolz.curry.
        return Just(f(self.value))


    @Function
    def apply_to(self, x):
        return x.map(self.value)


    def __repr__(self):
        return "Just({0})".format(self.value)


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Applicative):


    @Function
    def map(self, f):
        return self


    @Function
    def apply_to(self, x):
        return self


    def __repr__(self):
        return "Nothing"


@Function
def pure(x):
    return Just(x)
