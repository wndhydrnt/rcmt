import importlib.metadata

from .rcmt import options_from_config, run

try:
    __version__ = importlib.metadata.version(__name__)
except:
    __version__ = "develop"
