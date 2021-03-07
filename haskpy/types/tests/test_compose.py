from haskpy.testing import make_test_class
from haskpy import Compose, Maybe, Identity, Just


MaybeIdentity = Compose(Maybe, Identity)


TestMaybeIdentity = make_test_class(MaybeIdentity)


def test_maybe_identity_pure():
    assert MaybeIdentity.pure(42).decomposed == Maybe.pure(Identity.pure(42))
    return


def test_maybe_identity_apply():
    x = MaybeIdentity(Just(Identity(42)))
    f = MaybeIdentity(Just(Identity(lambda x: x + 1)))
    assert x.apply(f).decomposed == Just(Identity(43))
    return
