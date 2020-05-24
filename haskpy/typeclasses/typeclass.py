from haskpy import utils


class MetaType(type):

    def __repr__(cls):
        return cls.__name__


class Type(object, metaclass=MetaType):
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
