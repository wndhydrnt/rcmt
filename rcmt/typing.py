from typing import Callable

from rcmt import context

Action = Callable[[str, dict], None]
Matcher = Callable[[context.Context], bool]
