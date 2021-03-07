"""Profunctors

.. autosummary::
   :toctree:

   Profunctor

.. autosummary::
   :toctree:

   dimap

"""

from haskpy.types.function import function
from ._profunctor import Profunctor


@function
def dimap(f, g, x):
    """(a -> b) -> (c -> d) -> p b c -> p a d"""
    return x.dimap(f, g)
