from typing import Callable, Awaitable, Any

external_registry: dict[str, Callable[[Any,dict], Awaitable[None]]] = {}
internal_registry: dict[str, Callable[[Any,dict], Awaitable[None]]] = {}

def external_event(event_type: str):
    def decorator(func: Callable[[Any,dict], Awaitable[None]]):
        external_registry[event_type] = func
        return func
    return decorator


def internal_event(event_type: str):
    def decorator(func: Callable[[Any,dict], Awaitable[None]]):
        internal_registry[event_type] = func
        return func
    return decorator
