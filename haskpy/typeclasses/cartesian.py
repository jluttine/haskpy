"""Cartesian functors

.. autosummary::
   :toctree:

   Cartesian

"""

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._cartesian import Cartesian
Cartesian.__module__ = __name__
