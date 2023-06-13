import importlib.metadata

import rcmt.verify

from .rcmt import execute, options_from_config
from .task import Run, Task

__all__ = ["Run", "Task", "execute", "options_from_config"]

try:
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"
