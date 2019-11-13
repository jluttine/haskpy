from haskpy.functions import function


@function
def lens(view, update):
    """(s -> a) -> ((b, s) -> t) -> LensP a b s t

    where

    type LensP a b s t = Cartesian p => p a b -> p s t

    """

    def run(p):
        """LensP a b s t

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
