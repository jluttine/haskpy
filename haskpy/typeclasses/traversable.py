"""Traversable structure can be traversed, acccumulating results and effects

.. autosummary::
   :toctree:

   Traversable

"""

from hypothesis import strategies as st, given

from haskpy.typeclasses._functor import Functor
from haskpy.typeclasses.foldable import Foldable
from haskpy.types.function import function, compose
from haskpy.internal import class_function
from haskpy import testing
from haskpy.utils import identity


class Traversable(Functor, Foldable):
    """Data structures that can be traversed, accumulating results and effects

    Minimal complete definition::

        traverse | sequence

    """

    def traverse(self, applicative, func):
        """Map each element to an action and collect the results

        For ``Traversable t``::

            Applicative f => t a -> (a -> f b) -> f (t b)

        The default implementation is based on ``sequence``.

        """
        return self.map(func).sequence(applicative)

    def sequence(self, applicative):
        """Evalute each action in the structure and collect the results

        For ``Traversable t``::

            Applicative f => t (f a) -> f (t a)

        The default implementation is based on ``traverse``.

        """
        return self.traverse(applicative, identity)

    @class_function
    def sample_traversable_type_constructor(cls):
        return cls.sample_functor_type_constructor()

    @class_function
    @testing.assert_output
    def assert_traversable_traverse_naturality(cls, x, f, t, app_f, app_t):
        """Check naturality law of traverse"""
        return (
            t(x.traverse(app_f, f)),
            x.traverse(app_t, compose(t, f)),
        )

    @class_function
    @testing.assert_output
    def assert_traversable_sequence_naturality(cls, x, t, app_f, app_t):
        """Check naturality law of traverse"""
        from haskpy import map
        return (
            t(sequence(app_f, x)),
            sequence(app_t, map(t, x)),
        )

    @class_function
    @given(st.data())
    def test_traversable_naturality(cls, data):
        """Test naturality law of traverse

        .. note::

            The law should hold for every applicative transformation. However,
            we cannot create random applicative transformations with
            hypothesis, so the test uses a few manually written applicative
            transformations. The first one has type ``List a -> Either String
            a``, the second one ``Either _ a -> Maybe a``.

        See also
        --------

        assert_traversable_naturality

        """

        def check(app_trans, app1, app2):

            a = data.draw(testing.sample_hashable_type())
            b = data.draw(testing.sample_type())

            t = data.draw(cls.sample_traversable_type_constructor())
            f = data.draw(app1.sample_applicative_type_constructor())

            x = data.draw(t(a))
            g = data.draw(testing.sample_function(f(b)))

            cls.assert_traversable_traverse_naturality(
                x,
                g,
                app_trans,
                app1,
                app2,
                data=data,
            )
            cls.assert_traversable_sequence_naturality(
                x.map(g),
                app_trans,
                app1,
                app2,
                data=data,
            )
            return

        from haskpy.types.list import List
        from haskpy.types.either import Either, Left, Right

        # Applicative transformation: List a -> Either String a
        check(
            lambda xs: xs.last().match(
                Nothing=lambda: Left("foobar"),
                Just=lambda x: Right(x),
            ),
            List,
            Either,
        )

        from haskpy.types.maybe import Maybe, Just, Nothing

        # Applicative transformation: Either a b -> Maybe b
        check(
            lambda x: x.match(
                Left=lambda _: Nothing,
                Right=lambda x: Just(x),
            ),
            Either,
            Maybe,
        )

        return

    @class_function
    @testing.assert_output
    def assert_traversable_traverse_identity(cls, x):
        """Check identity law of traverse"""
        from haskpy.types.identity import Identity
        return (
            x.traverse(Identity, Identity),
            Identity(x),
        )

    @class_function
    @testing.assert_output
    def assert_traversable_sequence_identity(cls, x):
        """Check identity law of traverse"""
        from haskpy.types.identity import Identity
        from haskpy import map
        return (
            sequence(Identity, map(Identity, x)),
            Identity(x),
        )

    @class_function
    @given(st.data())
    def test_traversable_identity(cls, data):
        """Test identity law of traverse"""

        # Sample types
        a = data.draw(testing.sample_type())
        t = data.draw(cls.sample_traversable_type_constructor())

        # Sample values
        x = data.draw(t(a))

        # Check the laws
        cls.assert_traversable_traverse_identity(x, data=data)
        cls.assert_traversable_sequence_identity(x, data=data)
        return

    @class_function
    @testing.assert_output
    def assert_traversable_traverse_composition(cls, x, f, g, app_f, app_g):
        """Check composition law of traverse"""
        from haskpy.types.compose import Compose
        from haskpy import map, function
        f = function(f)
        g = function(g)
        Compose_ = Compose(app_f, app_g)
        return (
            traverse(Compose_, Compose_ ** map(g) ** f, x),
            Compose_(map(traverse(app_g, g), traverse(app_f, f, x))),
        )

    @class_function
    @testing.assert_output
    def assert_traversable_sequence_composition(cls, x, app_f, app_g):
        """Check composition law of sequence"""
        from haskpy.types.compose import Compose
        from haskpy import map
        Compose_ = Compose(app_f, app_g)
        return (
            sequence(Compose_, map(Compose_, x)),
            Compose_(map(sequence(app_g), sequence(app_f, x))),
        )

    @class_function
    @given(st.data())
    def test_traversable_composition(cls, data):
        """Test composition law of traverse"""
        # Sample an applicative type constructor
        from haskpy.typeclasses.applicative import Applicative
        app_f = data.draw(testing.sample_class(Applicative))
        app_g = data.draw(testing.sample_class(Applicative))

        # Sample types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_hashable_type())
        c = data.draw(testing.sample_type())
        t = data.draw(cls.sample_traversable_type_constructor())

        m_f = data.draw(app_f.sample_applicative_type_constructor())
        m_g = data.draw(app_g.sample_applicative_type_constructor())

        # Sample values
        x = data.draw(t(a))
        f = data.draw(testing.sample_function(m_f(b)))
        g = data.draw(testing.sample_function(m_g(c)))

        # Check the law
        from haskpy import map
        cls.assert_traversable_traverse_composition(x, f, g, app_f, app_g, data=data)
        cls.assert_traversable_sequence_composition(map(map(g), x.map(f)), app_f, app_g, data=data)
        return

    @class_function
    @testing.assert_output
    def assert_traversable_sequence(cls, app, x):
        return (
            Traversable.sequence(x, app),
            x.sequence(app),
            sequence(app, x),
        )

    @class_function
    @given(st.data())
    def test_traversable_sequence(cls, data):
        """Test sequence based on the default implementation

        The default implementation defines the law with respect to traverse.

        """
        # Sample an applicative type constructor
        from haskpy.typeclasses.applicative import Applicative
        app = data.draw(testing.sample_class(Applicative))

        # Sample types
        a = data.draw(testing.sample_hashable_type())
        t = data.draw(cls.sample_traversable_type_constructor())

        f = data.draw(app.sample_applicative_type_constructor())

        # Sample values
        x = data.draw(t(f(a)))

        # Check the law
        cls.assert_traversable_sequence(app, x, data=data)
        return

    @class_function
    @testing.assert_output
    def assert_traversable_traverse(cls, app, x, f):
        return (
            Traversable.traverse(x, app, f),
            x.traverse(app, f),
            traverse(app, f, x),
        )

    @class_function
    @given(st.data())
    def test_traversable_traverse(cls, data):
        """Test traverse based on the default implementation

        The default implementation defines the law with respect to sequence.

        """
        # Sample an applicative type constructor
        from haskpy.typeclasses.applicative import Applicative
        app = data.draw(testing.sample_class(Applicative))

        # Sample types
        a = data.draw(testing.sample_hashable_type())
        b = data.draw(testing.sample_hashable_type())
        t = data.draw(cls.sample_traversable_type_constructor())

        f = data.draw(app.sample_applicative_type_constructor())

        # Sample values
        x = data.draw(t(a))
        g = data.draw(testing.sample_function(f(b)))

        # Check the law
        cls.assert_traversable_traverse(app, x, g, data=data)
        return


@function
def traverse(applicative, g, x):
    """Map each element to an action and collect the results

    ::

        (Traversable t, Applicative f) => Applicative -> (a -> f b) -> t a-> f (t b)

    .. note::

        The first argument ``applicative`` is just a class that is contained
        inside the traversable structure. This needs to be provided so that the
        function can work consistently when the structure is empty. In Haskell,
        this information is provided by the type system.

    See also
    --------

    Traversable.traverse
    sequence

    """
    return x.traverse(applicative, g)


@function
def sequence(applicative, x):
    """Evalute each action in the structur and collect the results

    ::

        (Traversable t, Applicative f) => Applicative -> t (f a) -> f (t a)

    See also
    --------

    Traversable.sequence
    traverse

    """
    return x.sequence(applicative)
