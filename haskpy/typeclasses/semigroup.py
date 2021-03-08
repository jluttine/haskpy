"""Semigroups

.. autosummary::
   :toctree:

   Semigroup
   Commutative

"""

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._semigroup import Semigroup, Commutative
Semigroup.__module__ = __name__
Commutative.__module__ = __name__
