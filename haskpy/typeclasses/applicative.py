"""Applicatives

.. autosummary::
   :toctree:

   Applicative

"""

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._applicative import Applicative
Applicative.__module__ = __name__
