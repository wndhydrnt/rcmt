# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import glob
import os.path
from typing import Any, Generator


def iglob(root: str, selector: str) -> Generator[str, Any, None]:
    """
    iglob wraps glob.iglob to check if a selector escapes the root directory. Selecting
    files outside the root directory is not allowed and results in an exception.

    It also ensures that the returned Generator contains absolute paths only.

    :param root: Root path in which to select files.
    :param selector: The selector expression to pass to glob.iglob.
    :return: Generator[str]
    """
    root_abs_path = os.path.abspath(root)
    paths = glob.iglob(os.path.join(root, selector), recursive=True)
    for p in paths:
        abs_path = os.path.abspath(p)
        if abs_path.startswith(root_abs_path) is False:
            raise RuntimeError(f"Selector {selector} escapes root directory")

        yield abs_path
