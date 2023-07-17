from typing import Callable

from rcmt.source import source

Action = Callable[[str, dict], None]
Matcher = Callable[[source.Repository], bool]
