from haskpy.types.either import Either, Left, Right
from haskpy.testing import make_test_class


# Test typeclass laws for Either
TestEither = make_test_class(Either)


def test_either_match():
    """Make sure the given value is actually stored"""
    assert Left(42).match(Left=lambda x: x - 1, Right=lambda x: 666) == 41
    assert Right(42).match(Left=lambda x: 666, Right=lambda x: x + 1) == 43
    return


def test_either_map():
    """Make sure the originally given value isn't kept constant"""
    assert Right(42).map(lambda x: x + 1) == Right(43)
    return
