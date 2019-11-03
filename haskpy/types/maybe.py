import attr
import hypothesis.strategies as st
from hypothesis import given

from haskpy.typeclasses import Monad, CommutativeMonoid, PatternMatchable
from .monadtransformer import MonadTransformer
from haskpy.utils import singleton, sample_type, sample_sized


import functools
import inspect
def with_size(f):

    @functools.wraps(f)
    def wrapped(*args, size=None, **kwargs):
        return sample_sized(f(*args, **kwargs), size=size)

    return wrapped


def with_concrete_types(n):

    def wrap(f):

        @st.composite
        @functools.wraps(f)
        def wrapped(draw, cls, *args, **kwargs):
            types = (
                [arg for arg in args] +
                [
                    draw(st.from_type(type).map(st.from_type))
                    for i in range(n - len(args))
                ]
            )
            return draw(f(cls, *types, **kwargs))

        return wrapped

    return wrap


def sample_semigroup_type():
    from haskpy.types.monoids import String, Sum, And
    from haskpy.types import List
    return sample_type(
        types=[
            String.sample(),
            Sum.sample(),
            And.sample(),
        ],
        types1=[
            Maybe.sample,
            List.sample,
        ],
    )


def sample_commutative_type():
    from haskpy.types.monoids import Sum, And
    return sample_type(
        types=[
            Sum.sample(),
            And.sample(),
        ],
        types1=[
            Maybe.sample,
        ],
    )


class _MaybeMeta(type(Monad), type(CommutativeMonoid)):


    @property
    def empty(cls):
        return Nothing


    def pure(cls, x):
        return Just(x)


    @with_concrete_types(1)
    @with_size
    def sample(cls, a):
        return st.one_of(a.map(Just), st.just(Nothing))


    def sample_monoid(cls, **kwargs):
        # Any semigroup is ok as the type inside
        return sample_semigroup_type().flatmap(
            lambda t: cls.sample(t, **kwargs),
        )
        # return sample_type(
        #     types=[
        #         String.sample(),
        #         Sum.sample(),
        #         And.sample(),
        #     ],
        #     types1=[
        #         cls.sample,
        #         List.sample,
        #     ],
        # ).flatmap(lambda t: sample_sized(cls.sample(t), **kwargs))



    def sample_commutative(cls, **kwargs):
        # Any commutative semigroup is ok as the type inside
        from haskpy.types.monoids import Sum, And
        return sample_type(
            types=[
                Sum.sample(),
                And.sample(),
            ],
            types1=[
                cls.sample,
            ],
        ).flatmap(lambda t: sample_sized(cls.sample(t), **kwargs))


    # def sample(cls, a=None, **kwargs):
    #     from haskpy.types.list import List
    #     elements = (
    #         st.just(a) if a is not None else
    #         sample_type(
    #             types=[
    #                 st.integers(),
    #                 st.lists(st.integers()),
    #             ],
    #             types1=[
    #                 List.sample,
    #                 cls.sample,
    #             ]
    #         )
    #     )
    #     return elements.flatmap(
    #         lambda e: sample_sized(
    #             st.one_of(e.map(Just), st.just(Nothing)),
    #             **kwargs
    #         )
    #     )



# Some thoughts on design: One could implement all the methods (except match)
# in Maybe class by using the match method to choose the implementation. But
# this would be just clumsy and add overhead. Class inheritance is a Pythonic
# way of choosing the correct method implementation. Also, Just needs to
# support equality testing, so that's also easy to achieve by making it a
# class.


@attr.s(frozen=True, repr=False)
class Maybe(Monad, CommutativeMonoid, PatternMatchable, metaclass=_MaybeMeta):
    """Maybe type for optional values"""


    def match(self, *, Just, Nothing):
        raise NotImplementedError()


@attr.s(frozen=True, repr=False)
class Just(Maybe):


    __x = attr.ib()


    def match(self, *, Just, Nothing):
        return Just(self.__x)


    def map(self, f):
        return Just(f(self.__x))


    def apply_to(self, x):
        return x.map(self.__x)


    def bind(self, f):
        return f(self.__x)


    def append(self, m):
        return m.match(
            Nothing=lambda: self,
            Just=lambda x: Just(self.__x.append(x))
        )


    def __repr__(self):
        return "Just({0})".format(repr(self.__x))


@singleton
@attr.s(frozen=True, repr=False)
class Nothing(Maybe):


    def match(self, *, Just, Nothing):
        return Nothing()


    def map(self, f):
        return Nothing


    def apply_to(self, x):
        return Nothing


    def bind(self, f):
        return Nothing


    def append(self, m):
        return m


    def __repr__(self):
        return "Nothing"


@MonadTransformer(Maybe)
def MaybeT(BaseClass):


    @attr.s(frozen=True, repr=False)
    class Transformed(BaseClass):


        def join(self):
            """MaybeT m (MaybeT m a) -> MaybeT m a

            As decompressed:

              m (Maybe (m (Maybe a))) -> m (Maybe a)

            For instance,

            List(Just(List(Just(1), Nothing)), Nothing, Just(List(Nothing, Just(4))))

            -> List(Just(1), Nothing, Nothing, Nothing, Just(4))
            """
            cls = self.__class__
            return Transformed(
                self.decomposed.map(
                    lambda x: x.match(
                        Nothing=lambda: cls.OuterClass.pure(Nothing),
                        Just=lambda x: x.decomposed,
                    )
                ).join()
            )


        # def bind(self, f):
        #     """MaybeT m a -> (a -> MaybeT m b) -> MaybeT m b

        #     In decompressed terms:

        #       m (Maybe a) -> (a -> m (Maybe b)) -> m (Maybe b)

        #     """

        #     mMa = self.decompressed # :: m (Maybe a)

        #     # f :: a -> MaybeT m b
        #     # g :: Maybe a -> m (Maybe b)

        #     g = lambda Ma: Ma.map(f) # :: Maybe (MaybeT m b)


        #     y = self.decomposed.bind(g) # :: m (Maybe b)

        #     return Transformed(y) # :: MaybeT m b


    return Transformed


# class MaybeADT():


#     class Just():
#         __x = attr.ib()

#     @singleton
#     class Nothing():
#         pass

#     # or attrs programmatically

#     Just = case(lambda x: x)
#     Nothing = case(None)


#     def match(self, Just, Nothing):
#         pass


# class LinkedListADT():


#     Empty = case(None)
#     Cons = case(lambda x, xs: (x, xs))
