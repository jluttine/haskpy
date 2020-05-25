import sys
import hypothesis.strategies as st
from hypothesis import given


def make_test_class(C):
    """Fake PyTest to test class methods of a class

    When PyTest runs tests on a class, it creates an instance of the class and
    tests the instance. The class shouldn't have __init__ method. However, we
    want to test class methods, so there's no need to create an instance in the
    first place and it's ok to have any kind of __init__ method. To work around
    this PyTest limitation, we crete a class which doesn't have __init__ and
    when you call it's constructor, you actually don't get an instance of that
    class but instead the class that we wanted to test in the first place.
    PyTest thinks it got an instance of the class but actually we just gave it
    a class.

    So, to run the class method tests for a class SomeClass, add the following
    to some ``test_`` prefixed module:

    .. code-block:: python

        TestSomeClass = make_test_class(SomeClass)

    """

    dct = {
        name: getattr(C, name)
        for name in dir(C)
        if name.startswith("test_")
    }

    class MetaTestClass(type):

        __dict__ = dct

    class TestClass(metaclass=MetaTestClass):

        __dict__ = dct

        def __getattr__(self, name):
            return getattr(C, name)

    return TestClass


def is_pytest():
    return "pytest" in sys.modules


def pytest_configure(config):
    # Workaround for Hypothesis bug causing flaky tests if they use characters
    # or text: https://github.com/HypothesisWorks/hypothesis/issues/2108
    @given(st.text())
    def foo(x):
        pass
    foo()
    return

# PYTEST_RUNNING = False


# def pytest_configure(config):
#     global PYTEST_RUNNING
#     PYTEST_RUNNING = True
#     return


# def pytest_unconfigure(config):
#     global PYTEST_RUNNING
#     PYTEST_RUNNING = False
#     return
