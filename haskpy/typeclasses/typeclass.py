import attr
from haskpy import utils


class _MetaType(type):
    """Base metaclass for typeclasses

    .. note::

        There should be no need to import this class (or, in general, the
        metaclasses of other typeclasses, because you can access it as
        ``type(Type)`` (or whatever class you are interested in).

    """

    def __repr__(cls):
        return cls.__name__

    def sample(cls, *_, **__):
        raise NotImplementedError()

    @utils.nonexisting_function
    def __eq__(self, other):
        pass

    @utils.nonexisting_function
    def __ne__(self, other):
        pass

    @utils.nonexisting_function
    def __gt__(self, other):
        pass

    @utils.nonexisting_function
    def __ge__(self, other):
        pass

    @utils.nonexisting_function
    def __lt__(self, other):
        pass

    @utils.nonexisting_function
    def __le__(self, other):
        pass

    # Note that we aren't hiding __str__ here. That's because Sphinx converts
    # classes to strings when writing the documentation. This isn't a problem
    # really, because we are anyway more interested about the instances
    # (values) rather than the classes (types), so it's more important that we
    # don't have __str__ defined for the values.

    # IPython doesn't work properly if the type isn't hashable. See:
    # https://github.com/ipython/ipython/issues/12320
    #
    # See the workarounds in that issue or use normal Python REPL.
    @utils.nonexisting_function
    def __hash__(self, other):
        pass

    @property
    def __dict__(self):
        d = super().__dict__
        return {
            key: value
            for (key, value) in d.items()
            if key == "__dict__" or hasattr(self, key)
        }

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, utils.nonexisting_function):
            raise AttributeError()
        else:
            return attr


class Type(object, metaclass=_MetaType):
    """Foo"""

    def __dir__(self):
        xs = super().__dir__()
        return [
            x
            for x in xs
            if hasattr(self, x)
        ]

    @utils.nonexisting_function
    def __init__(self):
        pass

    @utils.nonexisting_function
    def __eq__(self, other):
        pass

    @utils.nonexisting_function
    def __ne__(self, other):
        pass

    @utils.nonexisting_function
    def __gt__(self, other):
        pass

    @utils.nonexisting_function
    def __ge__(self, other):
        pass

    @utils.nonexisting_function
    def __lt__(self, other):
        pass

    @utils.nonexisting_function
    def __le__(self, other):
        pass

    @utils.nonexisting_function
    def __str__(self):
        pass

    # IPython doesn't work properly if the type isn't hashable. See:
    # https://github.com/ipython/ipython/issues/12320
    #
    # See the workarounds in that issue or use normal Python REPL.
    @utils.nonexisting_function
    def __hash__(self, other):
        pass

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, utils.nonexisting_function):
            raise AttributeError()
        else:
            return attr

    def __test_eq__(self, x, data=None):
        """Equality used in unit tests

        For some types, such as functions, direct == doesn't work but one needs
        to compare the function outputs for many input points. Then, data can
        be useful. But for most cases, normal equality works just fine.

        """
        return self == x
