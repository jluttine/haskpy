import attr

from haskpy.typeclasses import Monad, PatternMatchable
from .monadtransformer import MonadTransformer
from haskpy.utils import singleton


class _MaybeMeta(type(Monad)):


    def pure(cls, x):
        return Just(x)


@attr.s(frozen=True)
class Maybe(Monad, PatternMatchable, metaclass=_MaybeMeta):


    def match(self, Just, Nothing):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Just(Maybe):


    value = attr.ib()


    def bind(self, f):
        return f(self.value)


    def map(self, f):
        return Just(f(self.value))


    def apply_to(self, x):
        return x.map(self.value)


    def match(self, Just, Nothing):
        return Just(self.value)


    def __repr__(self):
        return "Just({0})".format(repr(self.value))


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Maybe):


    def bind(self, f):
        return Nothing


    def map(self, f):
        return Nothing


    def apply_to(self, x):
        return Nothing


    def match(self, Just, Nothing):
        return Nothing()


    def __repr__(self):
        return "Nothing"


@MonadTransformer(Maybe)
def MaybeT(BaseClass):


    @attr.s(frozen=True, repr=False)
    class Transformed(BaseClass):


        def join(self):
            """MaybeT m (MaybeT m a) -> MaybeT m a

            As decompressed:

              m (Maybe (m (Maybe a))) -> m (Maybe a)

            For instance,

            List(Just(List(Just(1), Nothing)), Nothing, Just(List(Nothing, Just(4))))

            -> List(Just(1), Nothing, Nothing, Nothing, Just(4))
            """
            cls = self.__class__
            return Transformed(
                self.decomposed.map(
                    lambda x: x.match(
                        Nothing=lambda: cls.OuterClass.pure(Nothing),
                        Just=lambda x: x.decomposed,
                    )
                ).join()
            )


    return Transformed
