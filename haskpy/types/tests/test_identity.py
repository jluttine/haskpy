from haskpy import Identity, IdentityT, Function, List, Either
from haskpy.testing import make_test_class


# Test typeclass laws for Identity
TestIdentity = make_test_class(Identity)


def test_identity_map():
    """Make sure the originally given value isn't kept constant"""
    assert Identity(42).map(lambda x: x + 1) == Identity(43)
    return


TestIdentityT = make_test_class(IdentityT(Either))
TestIdentityT = make_test_class(IdentityT(List))
TestIdentityT = make_test_class(IdentityT(Function))
