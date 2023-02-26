# HaskPy - Haskell types and functions in Python

Hask is the category of types and functions in Haskell. This package provides
classes and functions inspired by Hask.

Documentation is available at [jluttine.github.io/haskpy](https://jluttine.github.io/haskpy/).

[![Test status](https://github.com/jluttine/haskpy/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/jluttine/haskpy/actions/workflows/test.yml)
[![Release](https://img.shields.io/pypi/v/haskpy.svg)](https://pypi.org/project/haskpy/)


## Overview

### Features

- Typeclasses: `Functor`, `Applicative`, `Monad`, `Semigroup`, `Monoid`,
  `Commutative`, `Foldable`, `Contravariant`, `Profunctor`, `Cartesian`,
  `Cocartesian`

  - **TODO:** `Traversable`, `Bifunctor`, `Monoidal`, `Ord`, `Show`, `Read`

- Types and type constructors: `Identity`, `Maybe`, `Either`, `List`,
  `Function`, `Compose`, `LinkedList`

  - **TODO:** `Constant`, `Validation`, `Dictionary`, `State`, `Reader`,
    `Writer`, `IO`

- Monad transformers: `MaybeT`, `IdentityT`

  - **TODO:** `StateT`, `ReaderT`, `WriterT`, `ListT`

- Simple monoids: `Sum`, `All`, `Any`, `String`, `Endo`

  - **TODO:** `Product`

- Profunctor optics: `adapter`, `lens`, `prism`

  - **TODO**: `traversal`, `grate`, `affine`, `setter`

- Operators for common tasks: ``**`` for function composition or functorial
  mapping, ``@`` for applicative application, ``%`` for monadic binding and
  ``>>`` for applicative/monadic sequencing.

- Property-based testing of typeclass laws

HaskPy has implemented typeclass laws as property-based tests. Thus, one can
easily test that an implementation satisfies all the laws it should. Just add
something like this to your test module and run with pytest:

```python
from haskpy.utils import make_test_class
from mystuff import MyClass
TestMyClass = make_test_class(MyClass)
```

This will automatically verify that `MyClass` satisfies all the typeclass laws
of those typeclasses that it inherits. It makes use of great [Hypothesis
package](https://hypothesis.readthedocs.io/en/latest/).


## Examples

### Functors

A minimal example of functorial mapping:

```python
>>> from haskpy import map, List
>>> map(lambda x: x**2, List(1, 2, 3, 4, 5))
List(1, 4, 9, 16, 25)
```

Lift over two layers of functorial structure:

```python
>>> from haskpy import map, List, Just, Nothing
>>> map(map(lambda x: x**2))(List(Just(1), Nothing, Just(3), Just(4), Nothing))
List(Just(1), Nothing, Just(9), Just(16), Nothing)
```

Note that `haskpy.map` works for all Functor instances. That is, you don't need
to use a different function to lift over different functors. You can even create
function that performs some operation to values contained in any two-layer
functorial structure. In the following example, `square` squares the values
inside a two-layer functor:

```python
>>> square = map(map(lambda x: x**2))
>>> square(List(Just(1), Nothing, Just(3)))
List(Just(1), Nothing, Just(9))
>>> square(List(List(1, 2, 3), List(4, 5)))
List(List(1, 4, 9), List(16, 25))
```

Even functions are functors if they have been decorated with `function`:

```python
>>> @function
... def f(x):
...     return List(x, 2*x, 3*x)
>>> square(f)(3)
List(9, 36, 81)
```

### Functions

HaskPy provides two different function types:

- `Function` for curried functions that only accept fixed number of positional
  arguments
- `Uncurried` for uncurried functions that are similar to Python functions in
  that they accept both positional and keyword arguments, and
  
Both of these types have, for instance, `Functor` and `Monad` implementations.
  
#### Curried functions

`Function` objects are curried and they should only take a fixed number of
positional arguments (at least one argument and no optional arguments).

Decorator `function` just converts a normal Python function into a curried
`Function` object:

```python
>>> from haskpy import function
>>> @function
... def concat(x, y, z):
...    return x + y + z
>>> concat("a")("b")("c")
"abc"
>>> concat("a")("b", "c")
"abc"
```

Note that it doesn't convert the function into nested one-argument functions (as
currying strictly speaking should do) but it gives more flexibility by accepting
any number of arguments (even no arguments at all), but the number of arguments
must be fixed. Keyword arguments aren't supported because of consistency.

Note also that nested functions can be treated as one multi-argument function:

``` python
>>> @function
... def prepend(x):
...     @function
...     def _run(y):
...         return x + y
...     return _run
>>> prepend("foo", "bar")
"foobar"
```

So, in terms of usability, a function with multiple arguments is identical to
nested functions. However, they might have performance differences - even
significant ones.

An example of lifting a multi-argument function over `Maybe`:

``` python
>>> concat ** Just("a") @ Just("b") @ Just("c")
Just("abc")
```

In terms of types, a function of multiple arguments is interpreted as a function
that takes only one argument and returns another function. This is important to
understand, for instance, when using operations such as functorial `map`: they
modify what the function returns after receiving the first argument - which in
case of a "multi-argument" function is a "partially applied" function.

Almost all functions in HaskPy have been decorated with `function`. It is
possible to use it to decorate methods too.


#### Uncurried (Python-like) functions

`Uncurried` objects represent uncurried functions, which are probably more
familiar to regular Python users. Uncurried functions don't support partial
application: you pass all the arguments in a single function call and the
function gets evaluated. That's it. Operations such as functorial `map` affect
the value the function returns given all the arguments:

```python
>>> from haskpy import uncurried
>>> @uncurried
... def line(x, k, b=0):
...     return k * x + b
>>> map(lambda y: -y)(line)(5, k=2, b=100)
-110
```

If you don't pass all the arguments, you'll get an error:

``` python
>>> map(lambda y: -y)(line)(5)
TypeError: line() missing 1 required positional argument: 'k'
```

This is very different from how `Function` works. In a way, this uncurried
function type is like a function that takes only one argument but this single
argument is a collection of positional and keyword arguments. The positional
arguments can be seen as a list (that can contain different types) and the
keyword arguments can be seen as a dictionary. So, the single argument is a
tuple of a list and a dictionary. Interestingly, in Python syntax, the function
arguments are wrapped in parentheses similarly as in tuples.

`Uncurried` might be preferred over `Function`, for instance, when you need
keyword arguments or varying number of positional arguments, or when operations
such as `map` should be applied only after all the arguments have been given.

## Copyright

Copyright (C) 2019-2021 Jaakko Luttinen

HaskPy is licensed under the MIT License. See LICENSE file for a text of the
license or visit http://opensource.org/licenses/MIT.
