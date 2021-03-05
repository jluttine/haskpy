"""A collection of typeclasses

Typeclasses for basic properties:

.. autosummary::
   :toctree:

   eq.Eq
   hashable.Hashable

Container-like typeclasses:

.. autosummary::
   :toctree:

   functor.Functor
   applicative.Applicative
   monad.Monad
   contravariant.Contravariant
   profunctor.Profunctor
   cartesian.Cartesian
   cocartesian.Cocartesian

Typeclasses for types that can be merged:

.. autosummary::
   :toctree:

   semigroup.Semigroup
   semigroup.Commutative
   monoid.Monoid

Struture that can be manipulated:

.. autosummary::
   :toctree:

   foldable.Foldable

Abstract base class of the typeclasses:

.. autosummary::
   :toctree:

   typeclass.Type

Read more at `Typeclassopedia <https://wiki.haskell.org/Typeclassopedia>`_.

"""
from .typeclass import Type
from .functor import Functor
from .applicative import Applicative
from .monad import Monad
from .contravariant import Contravariant
from .profunctor import Profunctor
from .cartesian import Cartesian
from .cocartesian import Cocartesian
from .semigroup import Semigroup, Commutative
from .monoid import Monoid
from .foldable import Foldable
from .hashable import *
from .eq import Eq
