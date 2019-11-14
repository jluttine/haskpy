import attr

from haskpy.types.either import Left, Right
from haskpy.optics import lens, prism


def test_lens_nested_structure():

    @attr.s(frozen=True)
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


def test_prism():

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
