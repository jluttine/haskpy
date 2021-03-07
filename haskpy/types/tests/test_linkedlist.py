from haskpy.types.linkedlist import LinkedList, Cons, Nil
from haskpy.testing import make_test_class


# Test typeclass laws for LinkedList
# from haskpy.typeclasses import Applicative
# TestList = make_test_class(LinkedList, [Applicative])
TestLinkedList = make_test_class(LinkedList)


def test_linkedlist_map():
    """Test functorial mapping of LinkedList

    Even if LinkedList followed the laws, it doesn't guarantee the desired
    behavior, so let's check that.

    """
    mapped = Cons(1, lambda: Cons(2, lambda: Nil)).map(lambda x: x * 10)
    expected = Cons(10, lambda: Cons(20, lambda: Nil))
    assert mapped == expected


def test_linkedlist_bind():
    """Test monadic bind of LinkedList

    Laws alone don't guarantee the desired behavior

    """
    def f(x):
        return Cons(x + 100, lambda: Cons(x + 200, lambda: Nil))
    xs = Cons(10, lambda: Cons(20, lambda: Nil))
    expected = Cons(
        110,
        lambda: Cons(
            210,
            lambda: Cons(
                120,
                lambda: Cons(
                    220,
                    lambda: Nil
                )
            )
        )
    )
    assert xs.bind(f) == expected


def test_linkedlist_eq():
    """Test equality of LinkedList

    Laws alone don't guarantee the desired behavior

    """
    x1 = Cons(10, lambda: Cons(20, lambda: Nil))
    x2 = Cons(10, lambda: Cons(20, lambda: Nil))
    y = Cons(10, lambda: Cons(30, lambda: Nil))
    assert x1 == x2
    assert x1 != y


def test_linkedlist_foldr():
    """Test right-associative fold of LinkedList

    Laws alone don't guarantee the desired behavior

    """
    xs = Cons(1, lambda: Cons(2, lambda: Nil))
    res = xs.foldr(lambda x: lambda acc: "({0}+{1})".format(x, acc), 0)
    assert res == "(1+(2+0))"
