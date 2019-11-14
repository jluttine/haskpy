from haskpy.functions import function, identity, either


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
