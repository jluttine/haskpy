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

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._applicative import Applicative
Applicative.__module__ = __name__


@function
def liftA2(f, x, y):
    return x.map(f).apply_to(y)


@function
def liftA3(f, x, y, z):
    return liftA2(f, x, y).apply_to(z)


@function
def apply(f, x):
    return x.apply(f)


@function
def sequence(x, y):
    return x.sequence(y)
