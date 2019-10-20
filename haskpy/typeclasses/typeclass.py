class TypeclassMeta(type):
    """Base metaclass for typeclasses"""


    def __repr__(cls):
        return cls.__name__
