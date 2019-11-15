from haskpy.conftest import make_test_class
from haskpy.types.monoids import Sum, And, Or, String, Endo


TestSum = make_test_class(Sum)

TestAnd = make_test_class(And)

TestOr = make_test_class(Or)

TestString = make_test_class(String)

TestEndo = make_test_class(Endo)
