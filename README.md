# HaskPy - Haskell types and functions in Python

Hask is the category of types and functions in Haskell. This package provides
classes and functions inspired by Hask.

**This is currently in planning phase, consider this a proof of concept.**


## Overview

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
functorial structure:

```python
>>> square_lifted2 = map(map(lambda x: x**2))
>>> square_lifted(List(Just(1), Nothing, Just(3)))
List(Just(1), Nothing, Just(9))
>>> square_lifted(List(List(1, 2, 3), List(4, 5)))
List(List(1, 4, 9), List(16, 25))
```

### Currying

HaskPy provides `curry` decorator which curries a function in such a way that
**the function remains partially evaluated until all required arguments have
been provided**:

```python
>>> from haskpy import curry
>>> @curry
... def concat(x, y, z):
...    return x + y + z
>>> concat("a")("b")("c")
"abc"
>>> concat("a")("b", "c")
"abc"
```

It doesn't convert the function into nested one-argument functions (as currying
strictly speaking should do) but it gives more flexibility by accepting any
number of arguments (even no arguments at all). It also handles keyword
arguments and any other optional arguments in an intuitive way similarly as
normal function calls.

It is very similar to the curry function in Toolz, but that implementation has
some critical design flaws (see
[toolz/#471](https://github.com/pytoolz/toolz/issues/471)). In addition to
correct behavior, the implementation of `haskpy.curry` is much simpler because
it doesn't need to support old Python versions. Here's a bit more complex usage
with keyword arguments:


```python
>>> @curry
... def concat_with_repeat(x, y, z, r=1):
...     return r*x + r*y + r*z
>>> concat_with_repeat(r=3)("a", "b")("c")
"aaabbbccc"
>>> concat_with_repeat(y="b")("a", z="c", r=2)
"aabbcc"
```

Note that positional arguments can be used as keyword arguments similarly as in
normal function calls.

### Functions

Instead of just currying a function, you may want to convert a function into an
object that has all the methods of functors, applicatives, monads and all other
typeclasses a function is an instance of. In that case, you can use `function`
decorator. Note that `function` also curries the function, so there's no need to
use `curry` in addition to `function`.

Almost all functions in HaskPy have been decorated with `function`.


## TODO

- Typeclasses:
  - Monad
  - Monoid
  - Foldable
  - Contravariant
  - Profunctor
  - Bifunctor
  - ...
- Types and type construtors:
  - Either
  - String
  - Dictionary (or HashMap)
  - Monad transformers
  - ...
- Profunctor optics


## Copyright

Copyright (C) 2019 Jaakko Luttinen

HaskPy is licensed under the MIT License. See LICENSE file for a text of the
license or visit http://opensource.org/licenses/MIT.
