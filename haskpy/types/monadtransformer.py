import attr

from haskpy.typeclasses import Monad
from .compose import Compose


def MonadTransformer(InnerMonad):

    def wrap(Constructor):

        def compose_with_monad(OuterMonad):

            X = Compose(OuterMonad, InnerMonad)


            class MetaClass(type):


                def __repr__(cls):
                    return "{0}({1})".format(
                        Constructor.__name__,
                        OuterMonad.__name__,
                    )


            @attr.s(frozen=True, repr=False)
            class BaseClass(X, Monad, metaclass=MetaClass):


                def __repr__(self):
                    return "{0}({1})".format(
                        repr(self.__class__),
                        repr(self.decomposed),
                    )


            return Constructor(BaseClass)

        return compose_with_monad

    return wrap
