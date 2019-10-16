import attr

from .applicative import Applicative
from haskpy.utils import function, identity


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


    @function
    def bind(self, f):
        """m a -> (a -> m b) -> m b

        Default implementation is based on ``join`` and ``map``:

        self :: m a

        f :: a -> m b

        map f :: m a -> m (m b)

        join :: m (m b) -> m b
        """
        return self.map(f).join()


    @function
    def join(self):
        """m (m a) -> m a

        Default implementation is based on ``bind``:

        self :: m (m a)

        identity :: m a -> m a

        bind :: m (m a) -> (m a -> m a) -> m a

        """
        return self.bind(identity)


    @function
    def apply(self, f):
        r"""m a -> m (a -> b) -> m b

        Default implementation is based on ``bind``:

        self :: m a

        f :: m (a -> b)

        g :: a -> m b
        g = \x -> map (\fh -> fh x) f

        """
        self.bind(lambda x: f.map(lambda fh: fh(x)))


@function
def bind(x, f):
    return x.bind(f)


@function
def join(x):
    return x.join()
