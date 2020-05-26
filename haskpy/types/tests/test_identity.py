from haskpy.types.identity import Identity, IdentityT
from haskpy.functions import Function
from haskpy.types import List
from haskpy.utils import make_test_class


# Test typeclass laws for Identity
TestIdentity = make_test_class(Identity)


def test_identity_map():
    """Make sure the originally given value isn't kept constant"""
    assert Identity(42).map(lambda x: x + 1) == Identity(43)
    return


TestIdentityT = make_test_class(IdentityT(List))
TestIdentityT = make_test_class(IdentityT(Function))
