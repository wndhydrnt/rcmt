# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import re
import shutil
import string
import subprocess
import tempfile
from typing import Optional, Union

import jinja2

from rcmt import Context, util


def absent(target: str) -> None:
    """Deletes a file or directory in a repository.

    Args:
        target: Path to the file or directory to delete.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import absent

        class Example(Task):
            def apply(ctx: Context) -> None:
                absent("file.txt")
        ```
    """
    if os.path.isfile(target):
        os.remove(target)
        return

    if os.path.isdir(target):
        shutil.rmtree(target)


def own(ctx: Context, content: str, target: str) -> None:
    """own ensures that a file in a repository stays the same.

    It overwrites the content of the file with the value of `content`.

    Args:
        ctx: The current context.
        content: Content of the file to write.
        target: Path to the file in a repository to own.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import own

        class Example(Task):
            def apply(ctx: Context) -> None:
                content = "[flake8]\\nmax-line-length = 88\\nextend-ignore = E203"
                own(content=content, target=".flake8")
        ```
    """
    with open(target, "w+") as f:
        f.write(string.Template(content).substitute(ctx.template_data))


def seed(ctx: Context, content: str, target: str) -> None:
    """Seed ensures that a file in a repository is present.

    It does not modify the file again if the file is present in a repository.

    Args:
        ctx: The current context.
        content: Path to the file in a repository to seed.
        target: A string or path to a file that contain the content to seed.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import seed

        class Example(Task):
            def apply(ctx: Context) -> None:
                # Ensure that the default Makefile is present.
                seed(content="foo:\n\t# foo", target="Makefile")
        ```
    """
    if os.path.isfile(target):
        return None

    own(ctx=ctx, content=content, target=target)


def exec(executable: str, args: Optional[list[str]] = None, timeout: int = 120) -> None:
    """exec calls an executable with the given arguments. The executable can then modify
    files. A common use case are code formatters such as black, prettier or "go fmt".

    The current working directory is set to the checkout of a repository.

    This action expects the executable it calls to have been installed already. It does
    not install the executable.

    Args:
        executable: Path to the executable.
        args: List of arguments to pass to the executable.
        timeout: Maximum runtime of the executable, in seconds.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import exec

        class Example(Task):
            def apply(ctx: Context) -> None:
                # Let black format all files in the current directory. The current
                # directory is the checkout of a repository.
                exec(executable="black", args=["--line-length", "120", "."])
        ```
    """
    _args: list[str] = args if args else []
    result = subprocess.run(
        args=[executable] + _args,
        capture_output=True,
        cwd=os.getcwd(),
        shell=False,
        timeout=timeout,
    )
    if result.returncode > 0:
        raise RuntimeError(
            f"""Exec action call to {executable} failed.
    stdout: {result.stdout.decode('utf-8')}
    stderr: {result.stderr.decode('utf-8')}"""
        )


def line_in_file(line: str, target: str) -> None:
    """line_in_file ensures that a line exists in a file. It adds the line if it does
    not exist.

    The line is always added at the end of the file.

    Args:
        line: Line to search for.
        target: The file to modify. Supports a glob pattern to modify multiple files.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import line_in_file

        class Example(Task):
            def apply(ctx: Context) -> None:
                line_in_file(line="The line", target="file.txt")
        ```
    """
    repo_file_paths = util.iglob(os.getcwd(), target)
    for path in repo_file_paths:
        with open(path, "r") as f:
            for current_line in f:
                if current_line.strip() == line:
                    return None

        with open(path, "a") as f:
            f.write(line)
            f.write("\n")


def delete_line_in_file(
    search: str, target: str, re_flags: Union[int, re.RegexFlag] = 0
) -> None:
    """delete_line_in_file deletes each line in a file that matches the regular
    expression `search`.

    Args:
        search: Regular expression to search for in each line of a file. Passed to
                `re.search`.
        target: The file to modify. Supports a glob pattern to modify multiple files.
        re_flags: Additional flags to pass to `re.search()`.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import delete_line_in_file

        class Example(Task):
            def apply(ctx: Context) -> None:
                delete_line_in_file(search="The line", target="file.txt")
        ```
    """
    regex = re.compile(pattern=search, flags=re_flags)
    repo_file_paths = util.iglob(os.getcwd(), target)
    for path in repo_file_paths:
        with open(path, "r") as f:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmpf:
                tmp_file_path = tmpf.name
                line_deleted = False
                for line in f:
                    if regex.search(line) is None:
                        tmpf.write(line)
                    else:
                        line_deleted = True

        if line_deleted:
            shutil.move(tmp_file_path, path)


def replace_in_line(
    ctx: Context,
    search: str,
    replace: str,
    target: str,
    re_flags: int = 0,
):
    """replace_in_line iterates over each line of a file and replaces a string if it
    matches a regular expression.

    It uses `re.sub()`.

    Args:
        ctx: The current context.
        search: Pattern to search for. This is a regular expression. Supports
                templating.
        replace: Replacement if `search` matches. Supports templating.
        target: The file to modify. Supports a glob pattern to alter multiple files.
        re_flags: Additional flags to pass to `re.sub()`.

    Example:
        ```python
        from rcmt import Task
        from rcmt.action import replace_in_line

        class Example(Task):
            def apply(ctx: Context) -> None:
                replace_in_line(
                    search="a test",
                    replace=r"an example",
                    target="file.txt",
                    flags=re.IGNORECASE,
                )
        ```
    """
    search_tpl = jinja2.Template(search)
    replace_tpl = jinja2.Template(replace)
    repo_file_paths = util.iglob(os.getcwd(), target)
    for repo_file_path in repo_file_paths:
        search = search_tpl.render(ctx.template_data)
        replace = replace_tpl.render(ctx.template_data)
        with open(repo_file_path, "r") as f:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmpf:
                for line in f:
                    tmpf.write(re.sub(search, replace, line, flags=re_flags))

        shutil.move(tmpf.name, repo_file_path)
