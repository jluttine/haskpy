# HaskPy - Haskell types and functions in Python

Hask is the category of types and functions in Haskell. This package provides
classes and functions inspired by Hask.

**This is currently in planning phase, consider this a proof of concept.**

Quite minimal example with two-layers of functor structure:

```python
>>> from haskpy import map, List, Just, Nothing
>>> map(map(lambda x: x**2))(List(Just(1), Nothing, Just(3), Just(4), Nothing))
List(Just(1), Nothing, Just(9), Just(16), Nothing)
```
