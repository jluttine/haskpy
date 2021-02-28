from haskpy.functions import Function, FunctionMonoid
from haskpy.utils import make_test_class
from haskpy.types.monoids import Sum


TestFunction = make_test_class(Function)


# Testing the Monoid instance requires some Monoid type. Otherwise, only
# Semigroup laws can be tested.
TestFunctionMonoid = make_test_class(FunctionMonoid(Sum))


def test_function_nesting():
    @Function
    def f(a, b, c):
        return a + b + c
    g1 = f("a")
    h1 = g1("b")
    assert h1("c") == "abc"
    g2 = Function(f("a"))
    h2 = Function(g2("b"))
    assert h2("c") == "abc"
