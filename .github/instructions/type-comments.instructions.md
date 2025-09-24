---
applyTo: "xen-bugtool"
---
# Type hints only in type comments

As we still support Python 2.7, we cannot use Python 3 type annotations.
As an alternative, we use type comments.
As type comments are not code, we shall use modern type hints in them.

## Details: Inside type comments, use modern type hints

We only use type checkers that understand modern type hints in type comments.

This includes:

- Type1 | Type2 union types
- list[Type] instead of List[Type]
- dict[KeyType, ValueType] instead of Dict[KeyType, ValueType]
- etc.

Type comments are not code, and only type checkers see them.
