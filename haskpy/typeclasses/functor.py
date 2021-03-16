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
    """Functor f => (a -> b) -> f a -> f b"""
    return x.map(f)


@function
def flap(f, x):
    """Functor f => f (a -> b) -> a - > f b

    Note that ``flap`` generalizes ``flip``:

    .. code-block:: python

        >>> flap(function(lambda a: lambda b: a - b), 4, 3)
        -1

    This is easy to see if you write use function type in the type signature::

        (c -> a -> b) -> a -> c -> b

    So, we just define ``flip = flap``.

    """
    return f.flap(x)


flip = flap


@function
def replace(a, x):
    return x.replace(a)
