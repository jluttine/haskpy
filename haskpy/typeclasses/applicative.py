"""Applicatives

.. autosummary::
   :toctree:

   Applicative

.. autosummary::
   :toctree:

   apply
   liftA2
   liftA3
   sequence

"""

from haskpy.types.function import function
from ._applicative import Applicative


@function
def liftA2(f, x, y):
    return x.map(f).apply(y)


@function
def liftA3(f, x, y, z):
    return liftA2(f, x, y).apply(z)


@function
def apply(f, x):
    return x.apply(f)


@function
def sequence(x, y):
    return x.sequence(y)
