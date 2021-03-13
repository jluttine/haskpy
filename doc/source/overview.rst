.. _overview:

Overview
========

Installing
**********

HaskPy can be installed, for instance, from PyPI:

.. code-block:: bash

   pip install haskpy

Development version is available at `GitHub
<https://github.com/jluttine/haskpy>`_.


The main contribution of HaskPy is to provide powerful types and typeclasses
inspired by Haskell. This section gives just a quick glimpse on some simple
usage, so refer to the API documentation for more detailed explanations.

If you just would like to know:

*Make duck typing much more powerful by using sound and powerful interfaces.*

*Make Python more pythonic with powerful base classes.*

This means that we can write code that is more generic and polymorphic.

To get started, import HaskPy:

.. code-block:: python

   >>> import haskpy as hp

Types
*****

For a full list of available types, refer to :py:mod:`haskpy.types` module. This
section highlights a few of the most important ones.

Maybe
-----

It is very common in programming to handle variables that might have a value or
not. In Python, this is typically done by using ``None`` to represent "no
value". With HaskPy, this can be represented by :py:class:`.Maybe` type with
:py:func:`.Just` constructor for values and :py:data:`.Nothing` for "no value".
This way you don't need to write if-else but you can treat the object similarly
regardless of whether it actually contains a value or not:

.. code-block:: python

    >>> inc = lambda v: v + 1
    >>> x = hp.Just(42)
    >>> x.map(inc)
    Just(43)
    >>> y = hp.Nothing
    >>> y.map(inc)
    Nothing

:py:class:`.Maybe` also helps you to avoid a common mistake that in some part of
the code you forget to take into account that a variable can be ``None`` too.
See :py:mod:`.maybe` for more details and examples.

Functions
---------

HaskPy provides decorator :py:func:`.function` to make functions more powerful.
The decorator converts the function into :py:class:`.Function` object which has
a lot more features than just being callable. For instance, it's a monad. In
addition, the function is curried in such a way that it can be called with any
number of arguments and it stays partially applied until all arguments have been
passed:

.. code-block:: python

    >>> f = hp.function(lambda x, y, z: x + y + z)
    >>> f("a")("b", "c")
    "abc"

Many of the methods (i.e., functions bound to objects) in HaskPy have
corresponding function counterparts. This is sometimes useful because functions
are easier to pass as arguments and only the functions have been decorated with
:py:func:`.function`. For instance, the example above could have been written
with :py:func:`.map` function:

.. code-block:: python

    >>> hp.map(inc, x)
    Just(43)
    >>> hp.map(inc, y)
    Nothing

To apply a two-argument function to values that are both inside
:py:class:`.Maybe` structure, one can use :py:func:`.liftA2`:

.. code-block:: python

    >>> add = hp.function(lambda a, b: a + b)
    >>> hp.liftA2(add, x, x)
    Just(84)
    >>> hp.liftA2(add, x, y)
    Nothing

See :py:class:`.Function` for more details and examples on HaskPy function type.
See :py:mod:`.utils` for a small collection of simple functions. Most functions
in the entire HaskPy package are imported so that they are available directly
under ``haskpy`` package as shown above with ``hp.map`` and ``hp.liftA2``.


List
----

:py:class:`List` is another basic type in HaskPy. Lists can be, for instance,
mapped:

.. code-block:: python

   >>> xs = hp.List(10, 20, 30)
   >>> hp.map(inc, xs)
   List(11, 21, 31)

and concatenated:

.. code-block:: python

   >>> ys = hp.List(40, 50)
   >>> hp.append(xs, ys)
   List(10, 20, 30, 40, 50)

For more details, see :py:mod:`.list`.

.. todo::

   Dictionary


Type signature
**************

Typeclasses
***********

For a full list of typeclasses, see :py:mod:`haskpy.typeclasses`. This section
highlights a few of the most important ones.

Functors, applicatives and monads
---------------------------------

I recommend that you read `"Functors, Applicatives, and Monads in Pictures"
<https://adit.io/posts/2013-04-17-functors,_applicatives,_and_monads_in_pictures.html>`_
for a good illustrated explanation about the concepts if you're not familiar
with them.

In short, :py:class:`.Functor` represents some kind of structure (think of it as
a container) that can contain values of some type in such a way that those
values can be modified without modifying the structure/container. This
modification of the values is called functorial mapping and :py:func:`.map` does
that. You've already seen a few examples above on how to use it for
:py:class:`.Maybe` and :py:class:`.List`, and also functions are functors.
Functor is an extremely common structure in programming. You can also lift over
a nested structure by using multiple maps:

.. code-block:: python

   >>> hp.map(hp.map(inc))(hp.List(hp.Just(42), hp.Nothing, hp.Just(100)))
   List(Just(43), Nothing, Just(101))

:py:class:`.Applicative` is a special case of :py:class:`.Functor`. Applicative
types know how to apply functions to values when both the functions and the
values are wrapped inside structure. This is done with :py:func:`.apply`
function:

.. code-block:: python

   >>> inc_maybe = hp.Just(inc)
   >>> hp.apply(inc_maybe, hp.Just(42))
   Just(43)
   >>> hp.apply(hp.Nothing, hp.Just(42))
   Nothing
   >>> square = hp.function(lambda v: v**2)
   >>> fs = hp.List(inc, square)
   >>> hp.apply(fs, hp.List(1, 10, 100))
   List(2, 11, 101, 1, 100, 10000)

Notice how with lists each function is applied to each value in the other list.
One common usecase for applicatives is a function that is applied to multiple
arguments that are all inside structure: map over the first argument, then the
partially applied function gets inside the structure, so all the remaining
arguments are applied with the applicative apply:

.. code-block:: python

   >>> add3 = hp.function(lambda a, b, c: a + b + c)
   >>> add3_a = hp.map(add3, hp.Just(42))
   >>> add3_ab = hp.apply(add3_a , hp.Just(100))
   >>> hp.apply(add3_ab, hp.Just(1))
   Just(143)

Or just :py:func:`.liftA3` for short:

.. code-block:: python

   >>> hp.liftA3(add3, hp.Just(42), hp.Just(100), hp.Just(1))
   Just(143)

Finally, :py:class:`.Monad` is a special case of :py:class:`.Applicative`.
Monads support yet another slightly different way of applying a function: the
argument is again inside a structure but the function itself isn't, only its
output. Alright, that might be a bit difficult to understand. Let's start from
the function. The following function inverts the given number, but it handles
zeros explicitly by using :py:class:`.Maybe`:

.. code-block:: python

   >>> invert = hp.function(lambda x: hp.Nothing if x == 0 else hp.Just(1/x))
   >>> invert(4)
   Just(0.25)
   >>> invert(0)
   Nothing

Given this function and a value that is also wrapped inside the same structure,
we can use :py:func:`.bind` function:

.. code-block:: python

   >>> hp.bind(hp.Just(10), invert)
   Just(0.1)
   >>> hp.bind(hp.Just(0), invert)
   Nothing
   >>> hp.bind(hp.Nothing, invert)
   Nothing

For more details, see :py:mod:`.functor`, :py:mod:`.applicative` and
:py:mod:`.monad` documentation. There are many other useful monads mentioned in
a section bit below.

Monoids
-------

:py:class:`.Monoid` is a typeclass for types whose values can be "merged". That
is, there's a binary operator that takes two arguments of the same type and
returns a result of that type.

.. code-block:: python

   >>> xs = hp.List(10, 20, 30)
   >>> ys = hp.List(40, 50)
   >>> hp.append(xs, ys)
   List(10, 20, 30, 40, 50)
   >>> s1 = hp.String("foo")
   >>> s2 = hp.String("bar")
   >>> hp.append(s1, s2)
   String('foobar')
   >>> u = hp.Just(hp.List(10, 20))
   >>> v = hp.Just(hp.List(30))
   >>> hp.append(u, v)
   Just(List(10, 20, 30))

Each monoid also has a class attribute called :py:attr:`.Monoid.empty` which is
an identity element of the binary operation. That is, combining value X with the
identity element gives X as the result:

.. code-block:: python

   >>> hp.append(xs, hp.List.empty)
   List(10, 20, 30)
   >>> hp.append(hp.String.empty, s2)
   String('bar')
   >>> hp.append(u, hp.Just.empty)
   Just(List(10, 20))

For more details, see :py:mod:`.monoid` and :py:mod:`.semigroup`. There are
also a few simple monoids implemented in :py:mod:`.monoids` such as
:py:class:`.All`.

Foldables
---------

:py:class:`.Foldable` is a typeclass for structure that can be "squashed", or
folded. It means that all the values in the structure can be processed into a
single value and the container structure disappears. The way that the values are
processed one by one can be controlled by the choice of the folding function
(e.g., :py:func:`.foldr`, :py:func:`.foldl`, :py:func:`.fold_map`).

For instance, to calculate the sum of the elements in a list:

.. code-block:: python

   >>> hp.foldl(lambda a: lambda b: a + b, 0, hp.List(1, 2, 3, 4))
   10

If the values in the container are of monoid type, you can use :py:func:`.fold`:

.. code-block:: python

   >>> hp.fold(hp.All, hp.List(hp.All(True), hp.All(True), hp.All(False)))
   All(False)

For more information, see :py:mod:`.foldable`. If you're interested in how to
fold infinite lists by short-circuiting and support tail-call optimization, see
:py:func:`.foldr_lazy`.

Traversables
------------

.. todo::

   Traversable. Show how to flip the structures.

Monad examples
--------------

.. todo::

   State, Reader, Writer

Operators
*********

Operators sometimes provide much nicer user experience than using functions.
However, Python has a fixed set of operators and one cannot define their own
operators, so one can use only the predefined ones. But using those operators
for a completely different purpose might be very confusing for the user as the
operators suddenly mean something totally different - or not, depending on the
context. Despite this major drawback, HaskPy defines new interpretations for a
few operators just to make it possible to write more compact code. However, it's
up to the user to decide whether it makes sense to use them or not.

Mapping can be done with ``**``:

.. code-block:: python

   >>> xs = hp.List(10, 20, 30)
   >>> inc = lambda x: x + 1
   >>> inc ** xs
   List(11, 21, 31)

Applicative applying is done with ``@``:

.. code-block:: python

   >>> ys = hp.List(1, 2)
   >>> add = lambda x: lambda y: x + y
   >>> add ** xs @ ys
   List(11, 12, 21, 22, 31, 32)

Applicative sequencing is done with ``>>``:

.. code-block:: python

   >>> xs >> ys
   List(1, 2, 1, 2, 1, 2)

Monadic binding is done with ``%``:

.. code-block:: python

   >>> hp.Just(10) % invert
   Just(0.1)

Monoid values are combined with ``+``:

.. code-block:: python

   >>> xs + ys
   List(10, 20, 30, 1, 2)

For more details about why these operators were chosen, see the documentation of
the operators :py:meth:`.Functor.__rpow__`, :py:meth:`.Applicative.__matmul__`,
:py:meth:`.Applicative.__rshift__`, :py:meth:`.Monad.__mod__` and
:py:meth:`.Semigroup.__add__`.

Algebraic data types (ADTs)
***************************

Algebraic data types (ADTs) are composite types constructed by using product and
sum types. A product type means that the values of that type contain values of
all the types in the product. A sum type means that the values of that type
contain a value of one of the types in the sum.

There are many ways to achieve this in Python, but in HaskPy the following
approach has been used in :py:class:`.Maybe` and :py:class:`.Either`: Define the
ADT as a class which has ``match`` method given as an argument when constructing
values. The sum type is represented by different function that create those
objects and the product type is represented by the arguments to those functions.

For instance, ``MyMaybe a = MyJust a | MyNothing`` can be represented as:

.. code-block:: python

   class MyMaybe():

       def __init__(self, match):
           self.match = match

   def MyJust(x):
       return MyMaybe(lambda *, MyJust, MyNothing: MyJust(x))

   MyNothing = MyMaybe(lambda *, MyJust, MyNothing: MyNothing())

The purpose of ``match`` method is simple pattern matching:

.. code-block:: python

   >>> inc_or_die = hp.match(
   ...     MyJust=lambda x: x + 1,
   ...     MyNothing=lambda: 666
   ... )
   >>> x = MyJust(42)
   >>> inc_or_die(x)
   43
   >>> y = MyNothing
   >>> inc_or_die(y)
   666

Note that with this kind of pattern matching, one is forced to provide a
function to handle each case so the pattern matching is total (no missed cases).

This definitely isn't the only way to construct ADTs in Python. A natural
alternative would be to use subclasses. With the approach shown above, it is
clear that ``MyJust`` and ``MyNothing`` are just data constructors, they cannot
add any methods of their own. That is ``MyJust`` and ``MyNothing`` have exactly
the same interface. This isn't forced when using subclasses where one could
define a method for ``MyNothing`` only. Also, the implementations of the methods
are split into multiple classes whereas with this approach all methods are
implemented in ``MyMaybe`` class and it's easy to see what the method does in
each case (see, for instance, the source of :py:class:`.Maybe`). With
inheritance, one might easily forget to implement some required methods in some
of the subclasses.

Profunctor optics
*****************

- :py:mod:`.optics`

Compose and monad transformers
******************************

monad transformers

Recursion
*********

recursion with tco and short-circuiting

Property-based testing
**********************
