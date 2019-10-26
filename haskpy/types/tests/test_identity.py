from haskpy.types.identity import Identity
from haskpy.conftest import make_test_class


# Test typeclass laws for Identity
TestIdentity = make_test_class(Identity)


def test_identity_map():
    """Make sure the originally given value isn't kept constant"""
    assert Identity(42).map(lambda x: x + 1) == Identity(43)
    return
