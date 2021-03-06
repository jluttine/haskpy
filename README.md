# HaskPy - Haskell types and functions in Python

Hask is the category of types and functions in Haskell. This package provides
classes and functions inspired by Hask.

Documentation is available at https://jluttine.github.io/HaskPy/

![Test status](https://github.com/jluttine/HaskPy/actions/workflows/test.yml/badge.svg?branch=master)

![Doc status](https://github.com/jluttine/HaskPy/actions/workflows/doc.yml/badge.svg)

![Release](https://img.shields.io/pypi/v/HaskPy.svg)


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

HaskPy provides type `Function` for functions so that they have, for instance,
`Functor` and `Monad` implementations. These functions are curried and they
should only take a fixed number of arguments (no optional arguments and at least
one argument). Decorator `function` just converts a normal Python function into
a curried `Function` object:

```python
>>> from haskpy import curry
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
any number of arguments (even no arguments at all). Keyword arguments aren't
supported because of consistency.

Almost all functions in HaskPy have been decorated with `function`.


## Copyright

Copyright (C) 2019-2021 Jaakko Luttinen

HaskPy is licensed under the MIT License. See LICENSE file for a text of the
license or visit http://opensource.org/licenses/MIT.
