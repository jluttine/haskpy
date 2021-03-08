"""Profunctor optics

.. currentmodule:: haskpy.optics

.. autosummary::
   :toctree:

   adapter
   lens
   prism

.. todo::

   traversal
   grate
   affine
   setter

Resources:

- Profunctor Optics: Modular Data Accessors by Pickering, Gibbons, and Wu
- Profunctor Optics: The Categorical View by Bartosz Milewski
- https://github.com/cmk/profunctor-extras/tree/master/profunctor-optics
- https://github.com/hablapps/DontFearTheProfunctorOptics
- http://oleg.fi/gists/images/optics-hierarchy.svg

"""


from haskpy.types.function import function
from haskpy.utils import identity


@function
def adapter(receive, send):
    """(s -> a) -> (b -> t) -> AdapterP a b s t

    where

    type AdapterP a b s t = Profunctor p => p a b -> p s t

    """

    def run(p):
        """(a -> b) -> s -> t, or more generally, AdapterP a b s t

        Profunctor p => p a b -> p s t

        """

        # For convenience, if we are given a plain Python function, let's wrap it
        # with our function decorator to get all the Profunctor goodies
        # automatically without the user needing to add the wrapping explicitly.
        # Just a usability improvement.
        if isinstance(p, type(lambda: 42)):
            p = function(p)

        return p.dimap(receive, send)

    return run


@function
def lens(view, update):
    """(s -> a) -> ((b, s) -> t) -> LensP a b s t

    where

    type LensP a b s t = Cartesian p => p a b -> p s t

    """

    @function
    def run(p):
        """(a -> b) -> s -> t, or more generally, LensP a b s t

        that is,

        Cartesian p => p a b -> p s t

        """

        # For convenience, if we are given a plain Python function, let's wrap it
        # with our function decorator to get all the Profunctor goodies
        # automatically without the user needing to add the wrapping explicitly.
        # Just a usability improvement.
        if isinstance(p, type(lambda: 42)):
            p = function(p)

        return p.first().dimap(lambda x: (view(x), x), update)

    return run


@function
def prism(match, build):
    """(s -> Either t a) -> (b -> t) -> PrismP a b s t

    where

    type PrismP a b s t = Cocartesian p => p a b -> p s t

    """

    # Just for easier user interface, wrap the given functions in case the user
    # didn't do that
    match = function(match)
    build = function(build)

    from haskpy.types.either import either

    @function
    def run(p):
        """(a -> b) -> s -> t, or more generally, PrismP a b s t

        that is,

        Cocartesian p => p a b -> p s t

        """
        # For convenience, if we are given a plain Python function, let's wrap it
        # with our function decorator to get all the Profunctor goodies
        # automatically without the user needing to add the wrapping explicitly.
        # Just a usability improvement.
        if isinstance(p, type(lambda: 42)):
            p = function(p)

        return p.right().dimap(match, either(identity, build))

    return run
