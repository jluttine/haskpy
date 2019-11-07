from haskpy.conftest import make_test_class
from haskpy.types.monoids import Sum, And, Or, String


TestSum = make_test_class(Sum)

TestAnd = make_test_class(And)

TestOr = make_test_class(Or)

TestString = make_test_class(String)

# TODO:
#
# sample_monoid_type() in all Monoid classes
#
# global level sample_any_monoid_type()
#
# global level sample_any_type()
#
# all classes: sample_type()
