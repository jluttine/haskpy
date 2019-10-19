import attr


class PatternMatchable():


    def match(self, **kwargs):
        raise NotImplementedError()


# PatternMatchable-related functions are defined in function module because of
# circular dependency.
