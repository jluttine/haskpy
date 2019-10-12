import attr
import toolz

from haskpy.function import Function as F
from haskpy.typeclasses.applicative import Applicative


@attr.s(frozen=True, repr=False)
class Function(Applicative):


    # For some reason, using toolz.curry wrapping for the function breaks the
    # following exmple:
    #
    # >>> haskpy.compose(pyhask.map, pyhask.map)(
    # ...     lambda x: 100*x,
    # ...     haskpy.Just(pyhask.List(1,2,3)),
    # ...     "these extra arguments",
    # ...     "should cause an error"
    # ... )
    #
    # Not sure if it's a problem not to have currying here..
    #
    # function = attr.ib(converter=toolz.curry)
    #
    # Anyway, we have to drop the currying here now:
    function = attr.ib(
        validator=lambda _, __, value: callable(value),
    )



    def __call__(self, *args, **kwargs):
        y = self.function(*args, **kwargs)
        return Function(y) if callable(y) else y


    @F
    def map(f, g):
        return Function(
            lambda *args, **kwargs: g(f(*args, **kwargs))
        )


    @F
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
        return getattr(self.function, name)


    def __repr__(self):
        return "Function {}".format(repr(self.function))
        return repr(self.function)
