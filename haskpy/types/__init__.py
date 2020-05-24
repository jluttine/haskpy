"""Types yey!

.. autosummary::
   :toctree: _autosummary

   List

"""
from .maybe import Maybe, Just, Nothing, MaybeT
from .either import Either, Left, Right
from .list import List
from .identity import Identity, IdentityT
from .compose import Compose
from .monoids import Sum, And, Or, String, Endo
