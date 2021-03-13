"""Apply typeclass

The name of the module is ``apply_`` instead of ``apply`` in order to avoid
name clashing with the function ``apply``.

.. autosummary::
   :toctree:

   Apply

.. autosummary::
   :toctree:

   apply
   apply_first
   apply_second
   lift2
   lift3
   lift4
   lift5

"""

from haskpy.types.function import function

# To avoid circular dependency, the class is defined in a hidden module. But
# import it as if it was defined in this module in order to fix references in
# Sphinx documentation.
from ._apply import Apply
Apply.__module__ = __name__


@function
def apply(f, x):
    """Apply f => f (a -> b) -> f a -> f b"""
    return x.apply(f)


@function
def apply_first(x, y):
    """Apply f => f a -> f b -> f a"""
    return x.apply_first(y)


@function
def apply_second(x, y):
    """Apply f => f a -> f b -> f b"""
    return x.apply_second(y)


@function
def lift2(f, a, b):
    """Apply f => (a -> b -> c) -> f a -> f b -> f c"""
    return a.map(f).apply_to(b)


@function
def lift3(f, a, b, c):
    return lift2(f, a, b).apply_to(c)


@function
def lift4(f, a, b, c, d):
    return lift3(f, a, b, c).apply_to(d)


@function
def lift5(f, a, b, c, d, e):
    return lift4(f, a, b, c, d).apply_to(e)
