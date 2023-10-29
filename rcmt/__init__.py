# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import importlib.metadata

from .context import Context
from .rcmt import execute, options_from_config
from .task import Task, register_task
from .validate import validate
from .verify import execute as execute_verify

__all__ = [
    "Context",
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
