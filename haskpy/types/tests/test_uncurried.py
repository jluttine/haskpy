from haskpy import UncurriedFunction, UncurriedFunctionMonoid, Sum
from haskpy.testing import make_test_class


TestUncurriedFunction = make_test_class(UncurriedFunction)


# Testing the Monoid instance requires some Monoid type. Otherwise, only
# Semigroup laws can be tested.
TestUncurriedFunctionMonoid = make_test_class(UncurriedFunctionMonoid(Sum))


def test_uncurried_function_apply():

    @UncurriedFunction
    def f(a, *_, b=42):
        return a + b

    @UncurriedFunction
    def g(a, *_, b=1):
        return lambda y: (a + b) * y

    assert (g @ f)(2) == 44 * 3
    assert (g @ f)(2, b=5) == 7 * 7

    return
