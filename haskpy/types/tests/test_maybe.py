from haskpy.types.maybe import Maybe, Just, Nothing, MaybeT
from haskpy.types import List
from haskpy.utils import make_test_class
from haskpy.functions import Function


# Test typeclass laws for Maybe
TestMaybe = make_test_class(Maybe)


def test_maybe_match():
    """Make sure the given value is actually stored"""
    assert Just(42).match(Nothing=lambda: 666, Just=lambda x: x) == 42
    assert Nothing.match(Nothing=lambda: 666, Just=lambda x: x) == 666
    return


def test_maybe_map():
    """Make sure the originally given value isn't kept constant"""
    assert Just(42).map(lambda x: x + 1) == Just(43)
    return


def test_maybe_foldl():
    """Make sure the folding is done as we expect"""
    assert Just("foo").foldl(lambda x: lambda y: x + y, "bar") == "barfoo"
    return


# Test typeclass laws for MaybeT monad transformer (using some example monad).
TestMaybeT = make_test_class(MaybeT(Function))
TestMaybeT = make_test_class(MaybeT(List))


def test_compose_vs_maybet():
    """Test the difference between MaybeT and Compose

    This was an interesting example that showed how MaybeT differs from Compose
    even for Applicative instance. So, MaybeT isn't a monadic extension of
    Compose, but rather it's.. well.. a monad transformer.

    """
    from haskpy.types import List, Compose

    MaybeList = MaybeT(List)
    xs = MaybeList(List(Nothing))
    ys = MaybeList(List(Just(1), Just(2)))
    assert xs.sequence(ys) == MaybeList(List(Nothing))

    MaybeList2 = Compose(List, Maybe)
    xs2 = MaybeList2(List(Nothing))
    ys2 = MaybeList2(List(Just(1), Just(2)))
    assert xs2.sequence(ys2) == MaybeList2(List(Nothing, Nothing))

    return
