from haskpy.types.list import List
from haskpy.testing import make_test_class


# Test typeclass laws for List
TestList = make_test_class(List)


def test_list_map():
    # Test that the list elements are correctly modified. Just obeying the laws
    # doesn't force that because, for instance, keeping values as constant
    # would be a trivial solution but not what we want here.
    assert List(1, 2, 3).map(lambda x: x * 10) == List(10, 20, 30)
    return


def test_list_apply():
    """Test apply puts values in desired order

    Again, the laws don't force the ordering but we want them in particular
    order.

    """
    assert List(1, 2).apply(List(lambda x: x+10, lambda x: x+100)) == \
        List(11, 12, 101, 102)


def test_list_foldr():
    # Foldable laws are tested already, but let's check that folding also does
    # what we expect, because the laws can be satisfied by some trivial
    # solutions too (e.g., foldr/foldl returns initial). There's nothing wrong
    # in such solutions, we just don't want those for our List. Also, these
    # test that the default implementations of Foldable are correct.
    assert "(a+(b+(c+x)))" == List("a", "b", "c").foldr(
        lambda x: lambda acc: "({0}+{1})".format(x, acc),
        "x"
    )
    return


def test_list_foldl():
    # Foldable laws are tested already, but let's check that folding also does
    # what we expect, because the laws can be satisfied by some trivial
    # solutions too (e.g., foldr/foldl returns initial). There's nothing wrong
    # in such solutions, we just don't want those for our List. Also, these
    # test that the default implementations of Foldable are correct.
    assert "(((x+a)+b)+c)" == List("a", "b", "c").foldl(
        lambda acc: lambda x: "({0}+{1})".format(acc, x),
        "x"
    )
    return
