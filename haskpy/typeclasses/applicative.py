import attr

from .functor import Functor


@attr.s(frozen=True)
class Applicative(Functor):


    @classmethod
    def pure(cls, x):
        raise NotImplementedError()



    def apply(self, f):
        return f.apply_to(self)


    def apply_to(self, x):
        return x.apply(self)


def liftA2(f, x, y):
    return x.map(f).apply(y)


def apply(f, x):
    return x.apply(f)
