import importlib.metadata

from .context import Context
from .rcmt import execute, options_from_config
from .task import Run, Task, register_task
from .validate import validate
from .verify import execute as execute_verify

__all__ = [
    "Context",
    "Run",
    "Task",
    "execute",
    "execute_verify",
    "options_from_config",
    "register_task",
    "validate",
]

try:
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"
