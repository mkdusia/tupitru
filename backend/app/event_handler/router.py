from typing import Callable, Awaitable, Type, TypeVar, Any
from pydantic import BaseModel
from app.event_handler.schemas.protocol import EventHandlerProtocol

T = TypeVar("T", bound=BaseModel)
HandlerFunc = Callable[[EventHandlerProtocol, T], Awaitable[None]]

external_registry: dict[str, tuple[Type[BaseModel], HandlerFunc[Any]]] = {}
internal_registry: dict[str, tuple[Type[BaseModel], HandlerFunc[Any]]] = {}


def external_event(
    event_type: str, schema: Type[T]
) -> Callable[
    [Callable[[EventHandlerProtocol, T], Awaitable[None]]],
    Callable[[EventHandlerProtocol, T], Awaitable[None]],
]:
    def decorator(func: HandlerFunc[T]) -> HandlerFunc[T]:
        external_registry[event_type] = (schema, func)
        return func

    return decorator


def internal_event(
    event_type: str, schema: Type[T]
) -> Callable[
    [Callable[[EventHandlerProtocol, T], Awaitable[None]]],
    Callable[[EventHandlerProtocol, T], Awaitable[None]],
]:
    def decorator(func: HandlerFunc[T]) -> HandlerFunc[T]:
        internal_registry[event_type] = (schema, func)
        return func

    return decorator
