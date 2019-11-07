from haskpy.typeclasses.typeclass import Type


class _HashableMeta(type(Type)):


    def sample_hashable_type(cls):
        return cls.sample_type()


class Hashable(Type, metaclass=_HashableMeta):
    pass
