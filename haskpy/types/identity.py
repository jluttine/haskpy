import attr

from haskpy.internal import class_function, immutable
from haskpy.typeclasses import Monad, Eq
from haskpy.testing import eq_test
from haskpy import testing


@immutable
class Identity(Monad, Eq):

    x = attr.ib()

    @class_function
    def pure(cls, x):
        return cls(x)

    def bind(self, f):
        """Identity a -> (a -> Identity b) -> Identity b"""
        return f(self.x)

    def __eq__(self, other):
        """Identity a -> Identity a -> bool"""
        return self.x == other.x

    def __repr__(self):
        return "Identity({})".format(repr(self.x))

    def __eq_test__(self, other, data):
        return eq_test(self.x, other.x, data)

    @class_function
    def sample_value(cls, a):
        return a.map(Identity)

    sample_type = testing.sample_type_from_value(
        testing.sample_type(),
    )

    sample_functor_type = testing.sample_type_from_value()
    sample_applicative_type = sample_functor_type
    sample_monad_type = sample_functor_type

    sample_eq_type = testing.sample_type_from_value(
        testing.sample_eq_type(),
    )


def IdentityT(M):

    class MetaIdentityM(type(Monad)):

        def __repr__(cls):
            return "IdentityT({})".format(repr(M))

    @immutable
    class IdentityM(Monad, metaclass=MetaIdentityM):

        decomposed = attr.ib()

        @class_function
        def pure(cls, x):
            return cls(M.pure(Identity.pure(x)))

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
            mib = mia.bind(g)

            return IdentityM(mib)  # :: IdentityT m b

        def __repr__(self):
            return "{0}({1})".format(repr(type(self)), repr(self.decomposed))

        def __eq_test__(self, other, data):
            return eq_test(self.decomposed, other.decomposed, data=data)

        @class_function
        def sample_type(cls):
            return (
                Identity.sample_type()
                .flatmap(M.sample_functor_type)
                .map(lambda s: s.map(cls))
            )

        @class_function
        def sample_functor_type(cls, a):
            return (
                Identity.sample_functor_type(a)
                .flatmap(M.sample_functor_type)
                .map(lambda s: s.map(cls))
            )

        @class_function
        def sample_applicative_type(cls, a):
            return (
                Identity.sample_applicative_type(a)
                .flatmap(M.sample_applicative_type)
                .map(lambda s: s.map(cls))
            )

        @class_function
        def sample_monad_type(cls, a):
            return (
                Identity.sample_monad_type(a)
                .flatmap(M.sample_monad_type)
                .map(lambda s: s.map(cls))
            )

        @class_function
        def sample_eq_type(cls):
            return (
                Identity.sample_eq_type()
                .flatmap(M.sample_monad_type)
                .map(lambda s: s.map(cls))
            )

    return IdentityM
