import attr

from haskpy.types.either import Left, Right
from haskpy.optics import adapter, lens, prism
from haskpy.utils import immutable


def test_adapter():
    """Test adapter composition"""

    scale = adapter(
        receive=lambda i: 10 * i,
        send=lambda i: i // 10,
    )
    int2str = adapter(
        receive=lambda i: str(i),
        send=lambda s: int(s),
    )

    # 42 -> 420 -> "420" -> "420420" -> 420420 -> 42042
    scale(int2str(lambda s: s + s))(42) == 42042

    return


def test_lens_composition():
    """Test composition of lenses"""

    @immutable(repr=True, eq=True)
    class Person():
        name = attr.ib()
        age = attr.ib()

    people = [Person("Alice", 42), Person("Bob", 7)]

    # Lens for accessing the first element of a list
    alice = lens(
        view=lambda xy: xy[0],
        update=lambda x_xy: [x_xy[0], x_xy[1][1]],
    )

    # Lens for accessing the age of a person
    age = lens(
        view=lambda p: p.age,
        update=lambda a_p: Person(name=a_p[1].name, age=a_p[0]),
    )

    # Compose the lenses and age increment
    birthday_alice = alice(age(lambda a: a + 1))

    # Apply the lens
    assert birthday_alice(people) == [
        Person("Alice", 43),
        Person("Bob", 7),
    ]

    return


def test_prism_composition():
    """Test composition of prisms"""

    none = prism(
        match=lambda x: Left(None) if x is None else Right(x),
        build=lambda x: x,
    )

    maybe_singleton = prism(
        match=lambda xs: Left(xs) if len(xs) == 0 else Right(xs[0]),
        build=lambda x: [x],
    )

    p = none(maybe_singleton(none(lambda x: x*10)))

    assert p([42]) == [420]
    assert p([]) == []
    assert p([None]) == [None]
    assert p(None) == None

    return


def test_lens_and_prism_composition():
    """Test composition of lenses and prisms"""

    def element(n):
        check_length = prism(
            match=lambda xs: Left(xs) if len(xs) <= n else Right(xs),
            build=lambda xs: xs,
        )
        pick = lens(
            view=lambda xs: xs[n],
            update=lambda x_xs: x_xs[1][:n] + [x_xs[0]] + x_xs[1][n+1:],
        )
        return lambda f: check_length(pick(f))

    first = element(0)
    third = element(2)
    op = lambda x: x * 10

    assert first(op)([1, 2, 3]) == [10, 2, 3]
    assert first(op)([42]) == [420]
    assert first(op)([]) == []
    assert third(op)([1, 2, 3, 4]) == [1, 2, 30, 4]
    assert third(op)([1, 2]) == [1, 2]

    return
