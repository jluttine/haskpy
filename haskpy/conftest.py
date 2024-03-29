import sys
import os
import hypothesis.strategies as st
from hypothesis import given, settings


settings.register_profile("dev", deadline=200)
settings.register_profile(name="ci", deadline=1000)

# By default, use dev profile
settings.load_profile(os.getenv(u"HYPOTHESIS_PROFILE", "dev"))


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
