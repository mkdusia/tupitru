from typing import Callable, Any, Awaitable


Emitter = Callable[[dict[str, Any]], Awaitable[None]]
