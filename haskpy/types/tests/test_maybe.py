from haskpy.types.maybe import Maybe, Just, Nothing, MaybeT
from haskpy.types import List
from haskpy.conftest import make_test_class


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


# Test typeclass laws for MaybeT monad transformer (using some example monad).
TestMaybeT = make_test_class(MaybeT(List))


def test_maybe_foldl():
    """Make sure the folding is done as we expect"""
    assert Just("foo").foldl(lambda x, y: x + y, "bar") == "barfoo"
    return
