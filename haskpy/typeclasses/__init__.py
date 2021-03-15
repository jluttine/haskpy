"""Typeclasses define properties that types may have.

Typeclass is a term used in Haskell. The term "typeclass" could roughly be
translated as "interface" in object-oriented programming languages. Each
typeclass defines some properties that a type can have, for instance, that
values of a type can be compared for equality (i.e, :py:class:`.Eq` typeclass).
Types can be instances of multiple typeclasses.

When a type implements an interface defined by a typeclass, the type is said to
be an instance of the typeclass in Haskell terminology. In HaskPy, the
typeclasses are implemented as base classes and the types inherit the
typeclasses. So, types are also classes and they aren't "instances" of
typeclasses but subclasses in Python terminology. However, we will use the
Haskellish terminology and say that types are instances of typeclasses although
they are implemented as subclasses.

Each typeclass can define methods or attributes that an instance must
implement. For instance, :py:class:`.Eq` instances must implement either
:py:meth:`.Eq.__eq__` or :py:meth:`.Eq.__ne__` method to tell how two values of
that type are compared for (in)equality. The typeclass can also define default
implementations for some of the methods. Each typeclass will tell what is the
minimum complete definition.

Parametric polymorphism means that a value can be of any type that is an
instance of some typeclass. For instance, function :py:func:`.eq` takes two
arguments that can be of any type that is an instance of :py:class:`.Eq`. But
because how the values should be compared, depends on the type the
implementation of :py:func:`.eq` depends on the type. This is achieved in a
pythonic way so that :py:func:`.eq` calls :py:meth:`.Eq.__eq__` method of the
first argument.

That is how parametric polymorphism in general is implemented in HaskPy. The
implementations are provided by methods/attributes of the type so Python can
find the correct implementation easily. Then, top-level functions act as thin
wrappers over these methods. For instance, :py:func:`.map` calls
:py:meth:`.Functor.map` method of the second argument and :py:func:`.bind`
calls :py:meth:`.Monad.bind` method of the first argument.

.. todo::

    Laws!

.. todo::

    Syntax! ``Eq a => a -> a -> Bool``


Typeclasses for basic properties:

.. autosummary::
   :toctree:

   equality
   ord
   hashable
   show
   readable

Container-like typeclasses:

.. autosummary::
   :toctree:

   functor
   apply_
   bind_
   applicative
   monad
   contravariant
   profunctor
   cartesian
   cocartesian
   bifunctor

Typeclasses for types that can be merged:

.. autosummary::
   :toctree:

   semigroup
   monoid

Struture that can be manipulated or traversed:

.. autosummary::
   :toctree:

   foldable
   traversable

Abstract base class of the typeclasses:

.. autosummary::
   :toctree:

   typeclass

Read more at `Typeclassopedia <https://wiki.haskell.org/Typeclassopedia>`_.

"""
from .typeclass import *
from .functor import *
from .apply_ import *
from .bind_ import *
from .applicative import *
from .monad import *
from .contravariant import *
from .profunctor import *
from .cartesian import *
from .cocartesian import *
from .semigroup import *
from .monoid import *
from .foldable import *
from .traversable import *
from .hashable import *
from .equality import *
