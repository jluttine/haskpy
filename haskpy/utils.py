"""Functions

.. autosummary::
   :toctree:

   identity
   const
   match

"""

from haskpy.types.function import function


@function
def identity(x):
    """a -> a"""
    return x


@function
def const(x, y):
    """a -> b -> a"""
    return x


#
# Pattern matching related functions
#
# NOTE: Currying doesn't work as expected for this function, because this is a
# generic function and we don't know how many arguments are required. We would
# first like to get all the required arguments and only after that the actual
# object on which to pattern match. One solution would be take the patterns as
# a dictionary. Then this function would always take two arguments and it would
# be explicit that all the patterns would be given at the same time. Something
# like:
#
def match(**kwargs):
    return lambda x: x.match(**kwargs)
