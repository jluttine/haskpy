import attr

from haskpy.utils import curry, function
from haskpy.typeclasses.applicative import Applicative


@attr.s(frozen=True, repr=False)
class Function(Applicative):


    f = attr.ib(
        converter=curry,
        validator=lambda _, __, value: callable(value),
    )


    def __call__(self, *args, **kwargs):
        y = self.f(*args, **kwargs)
        return Function(y) if callable(y) else y


    @function
    def map(f, g):
        return Function(
            lambda *args, **kwargs: g(f(*args, **kwargs))
        )


    @function
    def apply(f, g):
        return Function(
            lambda *args, **kwargs: g(*args, **kwargs)(f(*args, **kwargs))
        )


    def __getattr__(self, name):
        # Somehow toolz.curry messes up things a bit.. Without this __getattr__
        # function, the following example didn't raise an error as it should:
        #
        # >>> import haskpy
        # >>> haskpy.Function(pyhask.Function(lambda x, y: x+y))(1,2,3,4)
        #
        # Not sure if this is a good idea though. Now, these Function objects
        # may have all kind of weird attributes we don't have any control
        # over..
        return getattr(self.f, name)


    def __repr__(self):
        return repr(self.f)
