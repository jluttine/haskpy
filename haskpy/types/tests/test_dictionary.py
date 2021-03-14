from haskpy.testing import make_test_class
from haskpy import Dictionary


TestDictionary = make_test_class(Dictionary)


def test_dictionary_apply():
    """Test Dictionary.apply

    Laws don't guarantee a specific behavior, only consistent, so let's check
    that the output is what we want.

    """
    fs = Dictionary(
        foo=lambda x: x + 1,
        bar=lambda x: 2 * x,
    )
    xs = Dictionary(
        bar=42,
        baz=666,
    )
    assert (fs @ xs) == Dictionary(bar=84)
    return


def test_dictionary_eq():
    """Test Dictionary.eq

    Laws don't guarantee a specific behavior, only consistent, so let's check
    that the output is what we want.

    """
    assert Dictionary(foo=42) != Dictionary(bar=42)
    assert Dictionary(foo=42) != Dictionary(foo=666)
    assert Dictionary(foo=42) == Dictionary(foo=42)
    return
