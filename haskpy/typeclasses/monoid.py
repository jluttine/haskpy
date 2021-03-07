"""Monoids

.. autosummary::
   :toctree:

   Monoid

.. autosummary::
   :toctree:

   append

"""

from haskpy.types.function import function
from ._monoid import Monoid


@function
def append(x, y):
    """m -> m -> m"""
    return x.append(y)
