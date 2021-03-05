"""A collection of types

.. autosummary::
   :toctree:

   maybe
   either
   list
   linkedlist
   identity
   compose
   monoids

"""
from .maybe import Maybe, Just, Nothing, MaybeT
from .either import Either, Left, Right
from .list import List
from .linkedlist import LinkedList, Cons, Nil, iterate, repeat, replicate
from .identity import Identity, IdentityT
from .compose import Compose
from .monoids import Sum, All, Any, String, Endo
