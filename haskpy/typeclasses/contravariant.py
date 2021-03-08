"""Contravariant functors

.. autosummary::
   :toctree:

   Contravariant

.. autosummary::
   :toctree:

   contramap
   contrareplace

"""

from haskpy.types.function import function

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._contravariant import Contravariant
Contravariant.__module__ = __name__


@function
def contramap(f, x):
    """(a -> b) -> f b -> f a"""
    return x.contramap(f)


@function
def contrareplace(b, x):
    """b -> f b -> f a"""
    return x.contrareplace(b)
