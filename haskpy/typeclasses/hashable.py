"""Foo

"""

from haskpy.typeclasses.typeclass import Type
from haskpy.utils import abstract_class_function


class Hashable(Type):
    """Bar

    """

    @abstract_class_function
    def sample_hashable_type(cls):
        pass

    # TODO: Add tests!
