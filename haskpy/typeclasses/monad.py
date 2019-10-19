import attr

from .applicative import Applicative
from haskpy.utils import identity


@attr.s(frozen=True)
class Monad(Applicative):
    """Monad typeclass

    Minimum required implementations:

    - pure
    - one of the following:
      - bind
      - join and map

    The required Applicative methods are given default implementations based on
    the required Monad methods. But it is recommended to implement other
    methods as well if speed has any relevance.

    """


    def bind(self, f):
        """m a -> (a -> m b) -> m b

        Default implementation is based on ``join`` and ``map``:

        self :: m a

        f :: a -> m b

        map f :: m a -> m (m b)

        join :: m (m b) -> m b
        """
        return self.map(f).join()


    def join(self):
        """m (m a) -> m a

        Default implementation is based on ``bind``:

        self :: m (m a)

        identity :: m a -> m a

        bind :: m (m a) -> (m a -> m a) -> m a

        """
        return self.bind(identity)


    def apply(self, f):
        r"""m a -> m (a -> b) -> m b

          self :: m a

          f :: m (a -> b)

        Default implementation is based on ``bind`` and ``map``. In order to
        use ``bind``, we need to have a function of type:

          g :: a -> m b

        We can get this as follows:

          g = \x -> map (\fh -> fh x) f

        """
        return self.bind(lambda x: f.map(lambda fh: fh(x)))


    def map(self, f):
        """m a -> (a -> b) -> m b

        Default implementation is based on ``bind`` and ``pure``. This
        implementation needs to be provided because the default implementation
        of ``apply`` uses ``map``.

        """
        # Because of circular depdencies, need to import here inside
        from haskpy.functions import compose
        cls = type(self)
        return self.bind(compose(cls.pure, f))


# Monad-related functions are defined in function module because of circular
# dependency.
