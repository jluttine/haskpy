from haskpy.functions import Function, FunctionMonoid
from haskpy.utils import make_test_class
from haskpy.types.monoids import Sum


TestFunction = make_test_class(Function)


# Testing the Monoid instance requires some Monoid type. Otherwise, only
# Semigroup laws can be tested.
TestFunctionMonoid = make_test_class(FunctionMonoid(Sum))
