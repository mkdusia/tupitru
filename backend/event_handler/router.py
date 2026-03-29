from typing import Callable, Awaitable, Type, TypeVar
from pydantic import BaseModel
from event_handler.types.protocol import EventHandlerProtocol

T = TypeVar("T", bound=BaseModel)
HandlerFunc = Callable[[EventHandlerProtocol, T], Awaitable[None]]

external_registry: dict[str, tuple[Type[BaseModel], HandlerFunc]] = {}
internal_registry: dict[str, tuple[Type[BaseModel], HandlerFunc]] = {}

def external_event(event_type: str, schema: Type[T]):
    def decorator(func: HandlerFunc[T]) -> HandlerFunc[T]:
        external_registry[event_type] = (schema, func)
        return func
    return decorator


def internal_event(event_type: str, schema: Type[T]):
    def decorator(func: HandlerFunc[T]) -> HandlerFunc[T]:
        internal_registry[event_type] = (schema, func)
        return func
    return decorator
