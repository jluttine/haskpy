from haskpy.types.list import List
from haskpy.conftest import make_test_class


TestList = make_test_class(List)


def test_list_map():
    # Test that the list elements are correctly modified. Just obeying the laws
    # doesn't force that because, for instance, keeping values as constant
    # would be a trivial solution but not what we want here.
    assert List(1, 2, 3).map(lambda x: x * 10) == List(10, 20, 30)
    return
