from haskpy import Function, Type
from haskpy.internal import nonexisting_function, decorator


# class AbstractClassProperty():

#     def __repr__(self):
#         return "abstract class property"


def AbstractClassProperty(doc):
    @property
    def foo(bar):
        return
    foo.__doc__ = doc
    return foo


def preprocess_abstract_properties(obj):
    """Preprocess abstract properties

    Convert abstract properties into dummy properties that show up nicely in
    the documentation. Otherwise, the abstract properties will crash during
    sphinx build phase because inspect.getmembers accesses the attributes.

    """
    if isinstance(obj, type) and issubclass(obj, Type):
        for m in dir(obj):
            try:
                getattr(obj, m)
            except NotImplementedError:
                setattr(
                    obj,
                    m,
                    # We need to use a bit indirect way to get the docstring of
                    # the abstract property because we cannot just access the
                    # property directly.
                    AbstractClassProperty(obj.__dict__[m].__doc__),
                )
    return obj


def autodoc_before_process_signature(app, obj, bound_method):
    return preprocess_abstract_properties(obj)


def skip_tests(obj, name):
    return (
        name.startswith("test_") or
        name.startswith("assert_") or
        name.startswith("sample_")
    )


def skip_nonexisting(obj, name):
    return isinstance(obj, nonexisting_function)


def autodoc_skip_member(app, what, name, obj, skip, options):
    return (
        skip or
        skip_nonexisting(obj, name) or
        skip_tests(obj, name)
    )


def setup(app):

    # Add string support for types in order to make Sphinx documentation work.
    # Ugly mutation..
    setattr(Type, "__str__", Type.__repr__)

    # Monkey patching.. Autosummary doesn't detect decorated functions as
    # functions because they are Function instances. So, let's monkey patch the
    # function that autosummary uses to determine if it's a function or not. So
    # ugly..
    import inspect
    isfunction = inspect.isfunction
    inspect.isfunction = lambda f: (
        isfunction(f) or
        isinstance(f, Function) or
        isinstance(f, decorator)
    )

    # More monkey patching.. Decorated methods weren't shown correctly without
    # this.
    ismethod = inspect.ismethod
    inspect.ismethod = lambda f: (
        ismethod(f) or
        (inspect.isfunction(f) and hasattr(f, "__self__"))
    )

    app.connect(
        "autodoc-before-process-signature",
        autodoc_before_process_signature,
    )

    app.connect(
        "autodoc-skip-member",
        autodoc_skip_member,
    )

    return {}
