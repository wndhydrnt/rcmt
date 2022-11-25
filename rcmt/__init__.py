import importlib.metadata

from .rcmt import execute, execute_local, options_from_config
from .run import Run

__all__ = ["Run", "execute", "execute_local", "options_from_config"]

try:
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"
