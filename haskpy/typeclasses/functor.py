import attr


@attr.s(frozen=True)
class Functor():
    """Covariant functor"""


    def map(self, f):
        """Haskell fmap"""
        raise NotImplementedError()


    def replace(self, x):
        """Haskell ($>) operator"""
        return self.map(lambda _: x)


# Functor-related functions are defined in function module because of circular
# dependency.
