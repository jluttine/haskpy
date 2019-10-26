from haskpy.types.maybe import Maybe, Just, Nothing
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
