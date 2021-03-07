# Change log


## 0.2.0

### Added
- Add `Eq` typeclass.
- Add `LinkedList` type.

### Changed
- Mask out some built-in class methods such as `__eq__` and `__hash__`. Python
  doesn't allow deleting these methods so we need to do some black magic to hide
  them as if they didn't exist.
- Make `Function` objects curried and so that they only accept mandatory
  positional arguments.

### Fixed
- Fix the composition operator `**` for `Function` objects.

### Removed
- Remove `CommutativeMonoid`.
- Remove `curry` function.


## 0.1.3

### Fixed
- Fix PyPI releasing on GitHub


## 0.1.2

### Changed
- Improve operator docstrings.


## 0.1.1

### Changed
- Change bind operator to `%`.


## 0.1.0

### Added
- Add typeclasses `Functor`, `Applicative`, `Monad`, `Semigroup`, `Monoid`,
  `Commutative`, `CommutativeMonoid`, `Foldable`, `Contravariant`, `Profunctor`,
  `Cartesian`, `Cocartesian`.
- Add monads `Identity`, `Maybe`, `Either`, `List`, `Function`.
- Add transformers `Compose`, `MaybeT`, `IdentityT`.
- Add simple monoids `Sum`, `And`, `Or`, `String`, `Endo`
- Add profunctor optics `adapter`, `lens`, `prism`.
- Test typeclass laws with property-based testing.
- Add `curry`, `function`, `singleton`, `const`, `compose`, `identity` utility
  functions.
