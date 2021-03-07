"""Functors

.. autosummary::
   :toctree:

   Functor

.. autosummary::
   :toctree:

   map
   replace

"""

from haskpy.types.function import function
from ._functor import Functor


@function
def map(f, x):
    return x.map(f)


@function
def replace(a, x):
    return x.replace(a)
