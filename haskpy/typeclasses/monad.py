"""Monads are lovely

.. autosummary::
   :toctree:

   Monad

.. autosummary::
   :toctree:

   bind
   join

"""

from haskpy.types.function import function
from ._monad import Monad


@function
def bind(x, f):
    return x.bind(f)


@function
def join(x):
    return x.join()
