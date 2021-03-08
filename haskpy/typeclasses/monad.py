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

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._monad import Monad
Monad.__module__ = __name__


@function
def bind(x, f):
    return x.bind(f)


@function
def join(x):
    return x.join()
