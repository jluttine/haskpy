import pytest

from haskpy import utils
from haskpy.internal import (
    class_property,
    class_function,
    abstract_property,
    abstract_function,
    abstract_class_property,
    abstract_class_function,
)


def test_class_property():

    class A():

        @class_property
        def foo(cls):
            """Docstring of foo"""
            return 42

    assert A.foo == 42
    assert A.__dict__["foo"].__doc__ == "Docstring of foo"
    assert "foo" in dir(A)

    with pytest.raises(
            AttributeError,
            match="'A' object has no attribute 'foo'",
    ):
        A().foo

    with pytest.raises(KeyError, match="'foo'"):
        A().__dict__["foo"]

    # Unfortunately, by default __dir__ just adds all class attributes to
    # instances too. So, let's disable the test.

    # assert "foo" not in dir(A())

    return


def test_class_function():

    class A():

        @class_function
        def foo(cls, x, y):
            """Docstring of foo"""
            return x + y

    assert A.foo(10, 32) == 42
    assert A.foo.__doc__ == "Docstring of foo"
    assert "foo" in dir(A)

    with pytest.raises(
            AttributeError,
            match="'A' object has no attribute 'foo'",
    ):
        A().foo

    with pytest.raises(KeyError, match="'foo'"):
        A().__dict__["foo"]

    # Unfortunately, by default __dir__ just adds all class attributes to
    # instances too. So, let's disable the test.

    # assert "foo" not in dir(A())

    return


def test_abstract_function():

    class A():

        @abstract_function
        def foo(self, x, y):
            """Docstring of foo"""

    f = A.foo
    assert f.__doc__ == "Docstring of foo"
    assert "foo" in dir(A)
    with pytest.raises(
            NotImplementedError,
            match="'foo' function is abstract",
    ):
        f()

    g = A().foo
    assert g.__doc__ == "Docstring of foo"
    assert "foo" in dir(A())
    with pytest.raises(
            NotImplementedError,
            match="'foo' function is abstract",
    ):
        g()

    return


def test_abstract_property():

    class A():

        @abstract_property
        def foo(self):
            """Docstring of foo"""

    with pytest.raises(
            NotImplementedError,
            match="'foo' attribute of type object 'A' is abstract",
    ):
        A.foo

    with pytest.raises(
            NotImplementedError,
            match="'foo' attribute of object 'A' is abstract",
    ):
        A().foo

    assert A.__dict__["foo"].__doc__ == "Docstring of foo"

    assert "foo" in dir(A)
    assert "foo" in dir(A())

    return


def test_abstract_class_function():

    class A():

        @abstract_class_function
        def foo(cls, x, y):
            """Docstring of foo"""

    f = A.foo
    assert f.__doc__ == "Docstring of foo"
    assert "foo" in dir(A)
    with pytest.raises(
            NotImplementedError,
            match="'foo' function is abstract",
    ):
        f()

    with pytest.raises(
            AttributeError,
            match="'A' object has no attribute 'foo'",
    ):
        A().foo

    # Unfortunately, by default __dir__ just adds all class attributes to
    # instances too. So, let's disable the test.

    # assert "foo" not in dir(A())

    return


def test_abstract_class_property():

    class A():

        @abstract_class_property
        def foo(cls):
            """Docstring of foo"""

    assert A.__dict__["foo"].__doc__ == "Docstring of foo"
    assert "foo" in dir(A)
    with pytest.raises(
            NotImplementedError,
            match="'foo' attribute of type object 'A' is abstract",
    ):
        A.foo

    with pytest.raises(
            AttributeError,
            match="'A' object has no attribute 'foo'",
    ):
        A().foo

    # Unfortunately, by default __dir__ just adds all class attributes to
    # instances too. So, let's disable the test.

    # assert "foo" not in dir(A())

    return
