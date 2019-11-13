from haskpy.types.prism import prism
from haskpy.types.either import Left, Right


def test_prism():

    none = prism(
        match=lambda x: Left(None) if x is None else Right(x),
        build=lambda x: x,
    )

    maybe_singleton = prism(
        match=lambda xs: Left(xs) if len(xs) == 0 else Right(xs[0]),
        build=lambda x: [x],
    )

    p = none(maybe_singleton(none(lambda x: x*10)))

    assert p([42]) == [420]
    assert p([]) == []
    assert p([None]) == [None]
    assert p(None) == None

    return
