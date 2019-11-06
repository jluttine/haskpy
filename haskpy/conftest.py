import sys
import hypothesis.strategies as st


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


    class FakeConstructor(type):


        def __call__(cls):
            """Fake constructor to return the class we want, not instance"""
            return C


    class Fake(metaclass=FakeConstructor):
        """Fake() doesn't return an instance but the class we want to test"""
        pass


    return Fake


def is_pytest():
    return "pytest" in sys.modules


def pytest_configure(config):
    # Workaround for Hypothesis bug causing flaky tests if they use characters
    # or text: https://github.com/HypothesisWorks/hypothesis/issues/2108
    st.text().example()
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
