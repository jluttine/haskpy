from hypothesis import given
import hypothesis.strategies as st

from haskpy.testing import make_test_class
from haskpy import Sum, All, Any, String, Endo, Function
from haskpy import testing


TestSum = make_test_class(Sum)

TestAll = make_test_class(All)

TestAny = make_test_class(Any)

TestString = make_test_class(String)

TestEndo = make_test_class(Endo)


@given(st.data())
def test_function_type_in_endo(data):
    """Test functions as the input/output type of endo functions

    This needs to be written manually because functions aren't hashable so we
    cannot use them as the input type of functions automatically.

    Endofunction has type ``a -> a``. This test will use ``(a -> b) -> (a ->
    b)``.

    """

    def scale_output(f):
        def scaled(x):
            return f(x) * 3
        return Function(scaled)

    Endo.assert_monoid_identity(
        Endo(scale_output),
        data=data,
        input_strategy=testing.sample_function(st.integers())
    )

    def translate_output(f):
        def translated(x):
            return f(x) + 3
        return Function(translated)

    def exponentiate_output(f):
        def translated(x):
            return f(x) ** 3
        return Function(translated)

    Endo.assert_semigroup_associativity(
        Endo(scale_output),
        Endo(exponentiate_output),
        Endo(translate_output),
        data=data,
        input_strategy=testing.sample_function(st.integers())
    )

    return
