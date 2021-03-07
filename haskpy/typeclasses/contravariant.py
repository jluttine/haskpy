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
from ._contravariant import Contravariant


@function
def contramap(f, x):
    """(a -> b) -> f b -> f a"""
    return x.contramap(f)


@function
def contrareplace(b, x):
    """b -> f b -> f a"""
    return x.contrareplace(b)
