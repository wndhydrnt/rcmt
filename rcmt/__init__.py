import importlib.metadata

from .matcher import FileExists as FileExistsMatcher
from .matcher import RepoName as RepoNameMatcher
from .rcmt import execute, options_from_config
from .run import Run

try:
    __version__ = importlib.metadata.version(__name__)
except:
    __version__ = "develop"
