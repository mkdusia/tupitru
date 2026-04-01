import importlib
import pkgutil
from .handler import EventHandler


def load_modules(name: str) -> None:
    pkg = importlib.import_module(name)
    for _, name, _ in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        importlib.import_module(name)


load_modules("app.event_handler.external")
load_modules("app.event_handler.internal")


__all__ = ["EventHandler"]
