import attr
from haskpy import utils


@utils.immutable
class nonexisting():
    """Mark method non-existing

    This is a workaround for Python forcefully creating some methods. One
    cannot create objects that don't have ``__eq__``, ``__ge__``, ``__gt__``
    and many other methods. They are there and it's not possible to delete
    them. With this wrapper you can override those methods so that they won't
    show up in ``__dir__`` listing and if accessed in any way,
    ``AttributeError`` is raised. Note that it just hides the methods, one can
    still access them as ``object.__getattribute__(obj, "__eq__")``.

    """

    method = attr.ib()
    cls = attr.ib(default=None)

    def __call__(self, *args, **kwargs):
        name = self.method.__name__
        # The method doesn't exist
        raise TypeError(
            "No {0} function".format(name)
            if self.cls is None else
            "Class {0} has no {1} method".format(self.cls.__name__, name)
        )

    def __get__(self, obj, objtype):
        # Bind the method to a class
        return nonexisting(self.method, cls=objtype)


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

    @nonexisting
    def __eq__(self, other):
        pass

    @nonexisting
    def __ne__(self, other):
        pass

    @nonexisting
    def __gt__(self, other):
        pass

    @nonexisting
    def __ge__(self, other):
        pass

    @nonexisting
    def __lt__(self, other):
        pass

    @nonexisting
    def __le__(self, other):
        pass

    @nonexisting
    def __str__(self):
        pass

    # IPython doesn't work properly if the type isn't hashable. See:
    # https://github.com/ipython/ipython/issues/12320
    #
    # See the workarounds in that issue or use normal Python REPL.
    @nonexisting
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
        if isinstance(attr, nonexisting):
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

    @nonexisting
    def __eq__(self, other):
        pass

    @nonexisting
    def __ne__(self, other):
        pass

    @nonexisting
    def __gt__(self, other):
        pass

    @nonexisting
    def __ge__(self, other):
        pass

    @nonexisting
    def __lt__(self, other):
        pass

    @nonexisting
    def __le__(self, other):
        pass

    @nonexisting
    def __str__(self):
        pass

    # IPython doesn't work properly if the type isn't hashable. See:
    # https://github.com/ipython/ipython/issues/12320
    #
    # See the workarounds in that issue or use normal Python REPL.
    @nonexisting
    def __hash__(self, other):
        pass

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, nonexisting):
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
