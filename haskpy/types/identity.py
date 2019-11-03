import attr
import hypothesis.strategies as st

from haskpy.utils import sample_type, sample_sized
from haskpy.typeclasses import Monad
from .monadtransformer import MonadTransformer


class _IdentityMeta(type(Monad)):


    def pure(cls, x):
        return cls(x)


    def sample(cls, a=None, **kwargs):
        from haskpy.types import List
        elements = (
            st.just(a) if a is not None else
            sample_type(
                types=[
                    st.integers(),
                    st.lists(st.integers()),
                ],
                types1=[
                    List.sample,
                    cls.sample,
                ]
            )
        )
        return elements.flatmap(
            lambda e: sample_sized(e.map(Identity), **kwargs)
        )


@attr.s(frozen=True, repr=False)
class Identity(Monad, metaclass=_IdentityMeta):


    x = attr.ib()


    def bind(self, f):
        """Identity a -> (a -> Identity b) -> Identity b"""
        return f(self.x)


    def __repr__(self):
        return "Identity({})".format(repr(self.x))


@MonadTransformer(Identity)
def IdentityT(BaseClass):

    @attr.s(frozen=True, repr=False)
    class Transformed(BaseClass):


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

            return Transformed(y) # :: IdentityT m b


    return Transformed
