"""Profunctors

.. autosummary::
   :toctree:

   Profunctor

.. autosummary::
   :toctree:

   dimap

"""

from haskpy.types.function import function

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._profunctor import Profunctor
Profunctor.__module__ = __name__


@function
def dimap(f, g, x):
    """(a -> b) -> (c -> d) -> p b c -> p a d"""
    return x.dimap(f, g)
