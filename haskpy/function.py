import functools
import attr
import toolz


__all__ = [
    "Function",
    "compose",
]


@attr.s(frozen=True, repr=False)
class Function():


    function = attr.ib(
        # Would have been nice to use currying, but it just causes too many
        # issues apparently.. Main problem being you don't get errors when
        # doing something wrong but instead some really weird results. See, for
        # instance, https://github.com/pytoolz/toolz/issues/471
        #
        # converter=toolz.curry,
        validator=lambda _, __, value: callable(value),
    )


    def __call__(self, *args, **kwargs):
        # Forward the call to the underlying real Function class.
        #
        # In order to avoid circular imports, import Function here inside this
        # function.
        from haskpy.types._function import Function as F
        return F.__call__(self, *args, **kwargs)


    def __getattr__(self, name):
        # Forward the attribute query to the underlying real Function class.
        #
        # In order to avoid circular imports, import Function here inside this
        # function.
        from haskpy.types._function import Function as F
        return getattr(F(self.function), name)


    def __get__(self, obj, objtype):
        """Support instance methods.

        See: https://stackoverflow.com/a/3296318

        """
        return Function(functools.partial(self.__call__, obj))


    def __repr__(self):
        return "Function {}".format(repr(self.function))
        return repr(self.function)


@Function
def pure(x):
    return Function(lambda _: x)


@Function
def compose(g, f):
    return Function(f).map(g)
