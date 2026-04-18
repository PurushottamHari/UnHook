from typing import List, Tuple, Type

from injector import Scope, singleton

# Global registry to store classes decorated with @injectable
_REGISTRY: List[Tuple[Type, Scope]] = []


def injectable(scope: Scope = singleton):
    """
    Decorator to mark a class as injectable.
    Registered classes will be automatically bound to themselves in the DI container.
    """

    def decorator(cls: Type):
        # Check if already registered to avoid duplicates
        if not any(registered_cls == cls for registered_cls, _ in _REGISTRY):
            _REGISTRY.append((cls, scope))
        return cls

    return decorator
