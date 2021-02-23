import hypothesis.strategies as st
import attr

from haskpy.utils import singleton, immutable, class_function


def types():
    from haskpy import types
    from haskpy.types import hypothesis
    from haskpy.functions import Function
    # Some example types. The more types you add here, the longer it takes to
    # run the tests. Also, put simpler non-recursive strategies first:
    # https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.one_of
    return (
        types.And,
        hypothesis.HypothesisInteger,
        types.String,
        types.Maybe,
        # types.List,
        # Function,
    )


def sample_type_of(f, depth=0):

    def try_sample(cls):
        try:
            return f(cls)
        except AttributeError:
            return st.nothing()

    # NOTE: 1) Use deferring to work with the circular dependency in the type
    # modules: they import this module and types() function imports them. 2)
    # First select the type, then apply try_sample to it. If one would apply
    # try_sample to all types and then select one of the results, it would lead
    # to infinite recursion as all possible paths are traversed. 3) Use flatmap
    # instead of map!
    return st.deferred(
        lambda: st.sampled_from(types())
    ).flatmap(try_sample)


def sample_type():
    return sample_type_of(lambda cls: cls.sample_type())


def sample_hashable_type():
    return sample_type_of(lambda cls: cls.sample_hashable_type())


def sample_semigroup_type():
    return sample_type_of(lambda cls: cls.sample_semigroup_type())


def sample_monoid_type():
    return sample_type_of(lambda cls: cls.sample_monoid_type())


def sample_commutative_type():
    return sample_type_of(lambda cls: cls.sample_commutative_type())


def sample_eq_type():
    return sample_type_of(lambda cls: cls.sample_eq_type())


@st.composite
def sample_function(draw, b):
    return memoize(lambda _: draw(b))


def sample_class(typeclass):
    return st.sampled_from(
        tuple(filter(lambda cls: issubclass(cls, typeclass), types()))
    )


def sample_type_from_value(*arg_type_strategies):
    @class_function
    def sample(cls, *other_arg_value_strategies):
        y = st.tuples(*arg_type_strategies).map(
            lambda arg_value_strategies: cls.sample_value(
                *arg_value_strategies,
                *other_arg_value_strategies,
            )
        )
        return y
    return sample


@immutable
class memoize():

    __f = attr.ib()
    __memory = attr.ib(factory=list, init=False)

    def __call__(self, x):
        for (key, value) in self.__memory:
            if key == x:
                return value
        y = self.__f(x)
        self.__memory.append((x, y))
        return y
