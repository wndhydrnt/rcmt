import importlib.metadata

from .rcmt import execute, execute_local, options_from_config
from .task import Run, Task

__all__ = ["Run", "Task", "execute", "execute_local", "options_from_config"]

try:
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"
