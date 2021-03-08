"""Monoids

.. autosummary::
   :toctree:

   Monoid

.. autosummary::
   :toctree:

   append

"""

from haskpy.types.function import function

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._monoid import Monoid
Monoid.__module__ = __name__


@function
def append(x, y):
    """m -> m -> m"""
    return x.append(y)
