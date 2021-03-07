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
from .typeclass import *
from .functor import *
from .applicative import *
from .monad import *
from .contravariant import *
from .profunctor import *
from .cartesian import *
from .cocartesian import *
from .semigroup import *
from .monoid import *
from .foldable import *
from .hashable import *
from .eq import *
