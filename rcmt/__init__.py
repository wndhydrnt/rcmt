import importlib.metadata

from .rcmt import execute, options_from_config
from .task import Run, Task
from .validate import validate
from .verify import execute as execute_verify

__all__ = [
    "Run",
    "Task",
    "execute",
    "execute_verify",
    "options_from_config",
    "validate",
]

try:
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"
