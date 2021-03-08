"""Functors represent types that can be mapped over

.. autosummary::
   :toctree:

   Functor

.. autosummary::
   :toctree:

   map
   replace

"""

from haskpy.types.function import function

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._functor import Functor
Functor.__module__ = __name__


@function
def map(f, x):
    return x.map(f)


@function
def replace(a, x):
    return x.replace(a)
