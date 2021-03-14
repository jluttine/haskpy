Changelog
=========


Dev
***

Added
-----
- Add ``Dictionary`` type.
- Add ``Apply`` typeclass. In the typeclass hierarchy, it's between ``Functor``
  and ``Applicative``.
- Add ``+`` operator for ``Semigroup`` (and ``Monoid``) instances.
- Add ``<<`` operator for ``Apply`` (and ``Applicative``) instances.
- Add ``apply_first`` method to ``Apply``.
- Add ``lift4`` and ``lift5`` functions.

Changed
-------
- Rename ``sequence`` to ``apply_second``.
- Rename ``liftA2`` to ``lift2``.
- Rename ``liftA3`` to ``lift3``.
- Modify sampling for property tests. In particular, type constructors are
  sampled first, then those are used to sample concrete types. This way, other
  type constructor parameters are kept constant while the one of current
  interest can be modified.

Fixed
-----
- Fix ``liftA2`` and ``liftA3``.
- Complete ``Hashable`` typeclass.


0.2.0
*****

Added
-----
- Add ``Eq`` typeclass.
- Add ``LinkedList`` type.

Changed
-------
- Mask out some built-in class methods such as ``__eq__`` and ``__hash__``.
  Python doesn't allow deleting these methods so we need to do some black magic
  to hide them as if they didn't exist.
- Make ``Function`` objects curried and so that they only accept mandatory
  positional arguments.

Fixed
-----
- Fix the composition operator ``**`` for ``Function`` objects.

Removed
-------
- Remove ``CommutativeMonoid``.
- Remove ``curry`` function.


0.1.3
*****

Fixed
-----
- Fix PyPI releasing on GitHub


0.1.2
*****

Changed
-------
- Improve operator docstrings.


0.1.1
*****

Changed
-------
- Change bind operator to ``%``.


0.1.0
*****

Added
-----
- Add typeclasses ``Functor``, ``Applicative``, ``Monad``, ``Semigroup``,
  ``Monoid``, ``Commutative``, ``CommutativeMonoid``, ``Foldable``,
  ``Contravariant``, ``Profunctor``, ``Cartesian``, ``Cocartesian``.
- Add monads ``Identity``, ``Maybe``, ``Either``, ``List``, ``Function``.
- Add transformers ``Compose``, ``MaybeT``, ``IdentityT``.
- Add simple monoids ``Sum``, ``And``, ``Or``, ``String``, ``Endo``
- Add profunctor optics ``adapter``, ``lens``, ``prism``.
- Test typeclass laws with property-based testing.
- Add ``curry``, ``function``, ``singleton``, ``const``, ``compose``,
  ``identity`` utility functions.
