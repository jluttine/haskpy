from .functions import *
from .utils import *
from .typeclasses import *
from .types import *
from .optics import *
from . import autoclass

try:
    from importlib.metadata import version, PackageNotFoundError
except ModuleNotFoundError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass
