import glob
import os.path
from typing import Any, Generator, Union


def iglob(root: str, selector: str) -> Generator[str, Any, None]:
    """
    iglob wraps glob.iglob to check if a selector escapes the root directory. Selecting
    files outside the root directory is not allowed and results in an exception.

    It also ensures that the returned Generator contains absolute paths only.

    :param root: Root path in which to select files.
    :param selector: The selector expression to pass to glob.iglob.
    :return: Generator[str]
    """
    paths = glob.iglob(os.path.join(root, selector), recursive=True)
    for p in paths:
        abs_path = os.path.abspath(p)
        if abs_path.startswith(root) is False:
            raise RuntimeError(f"Selector {selector} escapes root directory")

        yield abs_path
