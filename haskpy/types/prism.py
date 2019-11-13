from haskpy.functions import function, identity, either


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
