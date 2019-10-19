import attr

from haskpy.function import function


class PatternMatchable():


    def match(self, **kwargs):
        raise NotImplementedError()


# NOTE: Currying doesn't work as expected for this function, because this is a
# generic function and we don't know how many arguments are required. We would
# first like to get all the required arguments and only after that the actual
# object on which to pattern match. One solution would be take the patterns as
# a dictionary. Then this function would always take two arguments and it would
# be explicit that all the patterns would be given at the same time. Something
# like:
#
# @function
# def match(patterns, x):
#     return x.match(**patterns)
#
# Is it better than:
@function
def match(**kwargs):
    return lambda x: x.match(**kwargs)
