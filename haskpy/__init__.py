"""Haskell and Hask category inspired utilities

.. autosummary::
   :toctree: _autosummary

   types
   typeclasses
   utils
   optics
   testing

"""

from .typeclasses import *
from haskpy.types.function import *
from haskpy.types.uncurried import *
from haskpy.types.maybe import *
from haskpy.types.either import *
from haskpy.types.list import *
from haskpy.types.linkedlist import *
from haskpy.types.dictionary import *
from haskpy.types.identity import *
from haskpy.types.compose import *
from haskpy.types.monoids import *
from .utils import *
from .optics import *

try:
    from importlib.metadata import version, PackageNotFoundError
except ModuleNotFoundError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass
