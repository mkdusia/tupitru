import importlib
import pkgutil

def load_modules(name: str):
    pkg = importlib.import_module(name)
    for _, name, _ in pkgutil.walk_packages(pkg.__path__, pkg.__name__+"."):
        importlib.import_module(name)

load_modules("event_handler.external")
load_modules("event_handler.internal")

from .handler import EventHandler
__all__ = ["EventHandler"]
