"""Cocartesian functors

.. autosummary::
   :toctree:

   Cocartesian

"""

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._cocartesian import Cocartesian
Cocartesian.__module__ = __name__
