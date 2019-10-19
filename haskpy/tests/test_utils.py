import pytest

from haskpy import utils


def test_curry():


    def run_check(f):
        def run(check):
            check(utils.curry(f))
            check(utils.curry(utils.curry(f)))
            # toolz.curry doesn't handle nesting properly and fails some of
            # these tests:
            g = lambda *args, **kwargs: utils.curry(f)(*args, **kwargs)
            check(g)
            check(utils.curry(g))
            check(utils.curry(utils.curry(g)))
            return
        return run


    @run_check(lambda: 10)
    def check_ten(f):
        assert f() == 10
        # Too many positional arguments
        with pytest.raises(TypeError):
            f(42)
        # Unknown keyword arguments
        with pytest.raises(TypeError):
            f(foo=42)
        return


    @run_check(lambda x, y: x - y)
    def check_x_minus_y(f):
        # Both as positional arguments
        assert f(5, 3) == 2
        assert f(5)(3) == 2
        # Partially applied function is also curried
        assert f()(5)(3) == 2
        assert f(5)()(3) == 2
        assert f()(5)()(3) == 2
        # Both as keyword arguments
        assert f(x=5, y=3) == 2
        assert f(y=3, x=5) == 2
        assert f(x=5)(y=3) == 2
        assert f(y=3)(x=5) == 2
        # x as positional, y as keyword
        assert f(5, y=3) == 2
        assert f(5)(y=3) == 2
        # x as keyword, y as positional
        with pytest.raises(TypeError):
            f(x=5)(3)
        # Too many arguments
        with pytest.raises(TypeError):
            f(5, 3, 1)
        with pytest.raises(TypeError):
            f(5)(3, 1)
        # Unknown keyword arguments
        with pytest.raises(TypeError):
            f(foo=2)
        with pytest.raises(TypeError):
            f(5)(foo=2)
        # Incorrect types for subtraction
        with pytest.raises(TypeError):
            f("foo", 5)
        return


    @run_check(lambda foo=42: foo + 1)
    def check_kw_only(f):
        assert f(foo=10) == 11
        assert f(10) == 11
        assert f() == 43
        with pytest.raises(TypeError):
            f(bar=10)
        with pytest.raises(TypeError):
            f(10, 11)
        with pytest.raises(TypeError):
            f(10, foo=11)
        return


    @run_check(lambda x, y=1: x - y)
    def check_x_minus_optional_y(f):
        # Only positional arguments
        assert f(5, 3) == 2
        assert f(5) == 4
        # Both as keyword arguments
        assert f(x=5, y=3) == 2
        assert f(y=3, x=5) == 2
        assert f(x=5) == 4
        assert f(y=3)(x=5) == 2
        # x as positional, y as keyword
        assert f(5, y=3) == 2
        # Too many arguments
        with pytest.raises(TypeError):
            f(5, 3, 1)
        with pytest.raises(TypeError):
            f(5)(3, 1)
        # Unknown keyword arguments
        with pytest.raises(TypeError):
            f(foo=2)
        with pytest.raises(TypeError):
            f(5)(foo=2)
        return


    @run_check(lambda x, *args: x + sum(args))
    def check_args(f):
        assert f(3) == 3
        assert f(x=3) == 3
        assert f(3, 4, 5) == 12
        assert f()()(3, 4, 5) == 12
        with pytest.raises(TypeError):
            f(4, 5, x=3)
        with pytest.raises(TypeError):
            f(foo=3)
        # toolz.curry fails TypeErrors when there are *args
        with pytest.raises(TypeError):
            f("foo", 42)
        return


    @run_check(lambda *args: sum(args))
    def check_args_only(f):
        assert f() == 0
        assert f(3, 4, 5) == 12
        with pytest.raises(TypeError):
            f(3, 4, foo=5)
        # toolz.curry fails TypeErrors when there are *args
        with pytest.raises(TypeError):
            f("foo", 42)
        return


    @run_check(lambda x, **kwargs: x + sum(kwargs.values()))
    def check_kwargs(f):
        assert f(3) == 3
        assert f(x=3) == 3
        assert f(3, y=4, z=5) == 12
        assert f(x=3, y=4, z=5) == 12
        assert f(y=4, z=5)(3) == 12
        assert f(y=4, z=5)(x=3) == 12
        return


    @run_check(lambda **kwargs: sum(kwargs.values()))
    def check_kwargs_only(f):
        assert f() == 0
        assert f(x=3) == 3
        assert f(x=3, y=4, z=5) == 12
        with pytest.raises(TypeError):
            f(3, 4, foo=5)
        return


    @run_check(lambda x, y, z: x + y + z)
    def check_three_args(f):
        # All positional
        assert f("a", "b", "c") == "abc"
        assert f("a", "b")("c") == "abc"
        assert f("a")("b", "c") == "abc"
        assert f("a")("b")("c") == "abc"
        # Use some keywords
        assert f(x="a")(y="b")(z="c") == "abc"
        assert f(x="a")(y="b", z="c") == "abc"
        assert f(y="b")("a", z="c") == "abc"
        assert f(z="c")("a", "b") == "abc"
        assert f(z="c")("a", y="b") == "abc"
        assert f(z="c")(y="b")("a") == "abc"
        # One can override keyword arguments later
        assert f(x="X")(x="a", y="b", z="c") == "abc"
        # Can't use positional arguments after keyword arguments
        with pytest.raises(TypeError):
            f(x="a")("b", "c")
        with pytest.raises(TypeError):
            f(y="b")("a", "c")
        return


    @run_check(lambda *args: (lambda x, y, z: x + y + z)(*args))
    def check_curried_decorator(f):
        assert f("a", "b", "c") == "abc"
        with pytest.raises(TypeError):
            f("a", "b")
        with pytest.raises(TypeError):
            f("a")
        with pytest.raises(TypeError):
            f("a", "b", "c", "d")
        pass


    # Invalid arguments to curry. (Note that curry itself isn't curried.)
    with pytest.raises(TypeError):
        utils.curry(42)
    with pytest.raises(TypeError):
        utils.curry("foo")
    with pytest.raises(TypeError):
        utils.curry()


    class some_function():


        def __init__(self, fail):
            self.counter = 0
            self.fail = fail
            return


        def __call__(self, *args, **kwargs):
            print(args, kwargs)
            self.counter += 1
            if self.fail:
                raise TypeError()


    curry4 = lambda f: utils.curry(utils.curry(utils.curry(utils.curry(f))))

    # The function is called only once on success
    f = some_function(fail=False)
    curry4(f)("foo", 1)
    assert f.counter == 1

    # The function is called only once on TypeError
    f = some_function(fail=True)
    fc = curry4(f)
    with pytest.raises(TypeError):
        fc(1, 2, 3, 4)
    assert f.counter == 1

    return
    return
