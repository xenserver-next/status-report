---
applyTo: "xen-bugtool"
---
# Inside type comments, use modern type hints

This includes:

- Type1 | Type2 union types
- list[Type] instead of List[Type]
- dict[KeyType, ValueType] instead of Dict[KeyType, ValueType]
- etc.

Type comments are not code, and only type checkers see them, not Python itself.

## Rationale

- We only use type checkers that understand modern type hints.
