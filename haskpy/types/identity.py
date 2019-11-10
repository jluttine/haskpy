import attr
import hypothesis.strategies as st

from haskpy.utils import sample_type, sample_sized
from haskpy.typeclasses import Monad


class _IdentityMeta(type(Monad)):


    def pure(cls, x):
        return cls(x)


    def sample_value(cls, a):
        return a.map(Identity)


@attr.s(frozen=True, repr=False)
class Identity(Monad, metaclass=_IdentityMeta):


    x = attr.ib()


    def bind(self, f):
        """Identity a -> (a -> Identity b) -> Identity b"""
        return f(self.x)


    def __repr__(self):
        return "Identity({})".format(repr(self.x))


def IdentityT(M):


    class _IdentityMMeta(type(Monad)):


        def pure(cls, x):
            return cls(M.pure(Identity.pure(x)))


        def sample_value(cls, a):
            return M.sample_value(Identity.sample_value(a)).map(cls)


        def __repr__(cls):
            return "IdentityT({})".format(repr(M))


    @attr.s(frozen=True, repr=False)
    class IdentityM(Monad, metaclass=_IdentityMMeta):


        decomposed = attr.ib()


        def bind(self, f):
            """IdentityT m a -> (a -> IdentityT m b) -> IdentityT m b

            In decomposed form, this is:

              m (Identity a) -> (a -> m (Identity b)) -> m (Identity b)

            Let's write the types of the relevant pieces:

              self :: IdentityT m a

              f :: a -> IdentityT m b

              decompose(self) :: m (Identity a)

              g :: Identity a -> m (Identity b)
              g = lambda ia: f(ia.x).decomposed

              y :: m (Identity b)
              y = decompose(self).bind(g)

              Transformed(y) :: IdentityT m b


            """
            # mia :: m (Identity a)
            mia = self.decomposed

            # g :: Identity a -> m (Identity b)
            g = lambda ia: f(ia.x).decomposed

            # y :: m (Identity b)
            y = self.decomposed.bind(g)

            return IdentityM(y) # :: IdentityT m b


        def __repr__(self):
            return "{0}({1})".format(repr(type(self)), repr(self.decomposed))


    return IdentityM
