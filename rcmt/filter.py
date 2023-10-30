# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re

from rcmt.context import Context


def file_exists(ctx: Context, path: str) -> bool:
    """file_exists returns `True` if a file at the given `path` exists in a repository.

    The code checks for the existence of a file by calling the API of the Source host.
    This prevents useless checkouts of repositories and saves bandwidth.

    Args:
        ctx: The current context.
        path: Path to the file, relative to the root of the repository. Supports a
              wildcard in the name of the file, e.g. `dir/*.json`.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import file_exists

        class Example(Task):
            def filter(ctx: Context) -> bool:
                return file_exists(ctx=ctx, path="pyproject.toml")
        ```
    """
    return ctx.repo.has_file(path)


def line_in_file(ctx: Context, path: str, search: str) -> bool:
    """line_in_file returns `True` if a line in a file of a repository matches a regular
    expression.

    It downloads the file from the repository without checking out the whole repository.

    Args:
        ctx: The current context.
        path: Path of the file to check.
        search: Regular expression to test against each line in the file.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import line_in_file

        class Example(Task):
            def filter(ctx: Context) -> bool:
                return file_exists(ctx=ctx, path=".gitignore", search="^\\.vscode?")
        ```
    """
    try:
        content = ctx.repo.get_file(path)
        for line in content.readlines():
            if re.match(pattern=search, string=line) is not None:
                return True

        return False
    except FileNotFoundError:
        return False


def repo_name(ctx: Context, search: str) -> bool:
    """repo_name returns `True` if the name of a repository matches a regular
    expression.

    Args:
        ctx: The current context.
        search: Regular expression to test against names of repositories.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import repo_name

        class Example(Task):
            def filter(ctx: Context) -> bool:
                return repo_name(ctx=ctx, search="^github.com/wndhydrnt/.*")
        ```
    """
    if re.match(pattern=search, string=ctx.repo.full_name) is None:
        return False

    return True
