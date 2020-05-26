import sys
import hypothesis.strategies as st
from hypothesis import given


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
