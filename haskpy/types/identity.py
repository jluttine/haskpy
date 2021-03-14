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

    sample_type = testing.create_type_sampler(
        testing.sample_type(),
    )

    sample_functor_type_constructor = testing.create_type_constructor_sampler()

    # Some typeclass instances have constraints for the types inside

    sample_eq_type = testing.create_type_sampler(
        testing.sample_eq_type(),
    )


def IdentityT(M):

    class MetaIdentityM(type(Monad)):

        def __repr__(cls):
            return "IdentityT({})".format(repr(M))

    is_eq = issubclass(M, Eq)

    bases = [] + (
        [Eq] if is_eq else []
    )

    @immutable
    class IdentityM(Monad, *bases, metaclass=MetaIdentityM):

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

        if is_eq:
            def __eq__(self, other):
                return self.decomposed == other.decomposed

        def __repr__(self):
            return "{0}({1})".format(repr(type(self)), repr(self.decomposed))

        def __eq_test__(self, other, data):
            return eq_test(self.decomposed, other.decomposed, data=data)

        @class_function
        def sample_type(cls):
            return M.sample_monad_type_constructor().map(
                lambda m: m(Identity.sample_type()).map(cls)
            )

        if is_eq:
            @class_function
            def sample_eq_type(cls):
                return M.sample_monad_type_constructor().map(
                    # Note that we can't be really sure if the Eq instance of M
                    # has any constraints for the contained type (i.e., Maybe
                    # in this case). A simple pathological monad M could be
                    # such that it totally ignores the contained type. However,
                    # it's the most typical case that M requires the contained
                    # type to be an instance of Eq too, so let's assume so.
                    # There's no real harm as this is only sampling for tests
                    # so it means we just use a bit more limited set of
                    # samples. But in practice, this is almost always needed.
                    #
                    # We could perhaps refactor the sampling methods so that we
                    # could write something like:
                    #
                    #     lambda m: m.sample_eq_type(Identity).map(cls)
                    #
                    # That is, m will decide how to constrain the sampling.
                    lambda m: m(Identity.sample_eq_type()).map(cls)
                )

        @class_function
        def sample_functor_type_constructor(cls):
            # This is a Monad transformer class, so let's sample monads even
            # when functors are required.
            return Identity.sample_monad_type_constructor().flatmap(
                lambda f: M.sample_monad_type_constructor().map(
                    lambda g: lambda a: g(f(a)).map(cls)
                )
            )

    return IdentityM
