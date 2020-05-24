"""Typeclasses yey!

.. autosummary::
   :toctree: _autosummary

   Type
   Functor
   Applicative
   Monad
   Monoid
   CommutativeMonoid

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
from .monoid import Monoid, CommutativeMonoid
from .foldable import Foldable
from .hashable import *
from .eq import Eq
