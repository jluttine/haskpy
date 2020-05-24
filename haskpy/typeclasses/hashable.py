from haskpy.typeclasses.typeclass import Type
from haskpy.utils import class_function


class Hashable(Type):

    @class_function
    def sample_hashable_type(cls):
        return cls.sample_type()
