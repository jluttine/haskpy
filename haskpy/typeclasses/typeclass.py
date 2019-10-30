class TypeclassMeta(type):
    """Base metaclass for typeclasses"""


    def __repr__(cls):
        return cls.__name__


    def assert_equal(cls, map, x, y):
        assert map(x) == map(y)
        return
