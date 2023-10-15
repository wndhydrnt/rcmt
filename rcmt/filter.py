# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re

from rcmt.context import Context
from rcmt.typing import Filter


class Base:
    """Base class that describes the methods of a Filter."""

    def __call__(self, ctx: Context) -> bool:
        return self.filter(ctx)

    def __repr__(self) -> str:
        args: list[str] = []
        for k, v in self.__dict__.items():
            if k.startswith("_") is True:
                continue

            args.append(f"{k}={v}")

        return f'{self.__class__.__name__}({", ".join(args)})'

    def filter(self, ctx: Context) -> bool:
        """Determine if a Task applies to a repository.

        Args:
            ctx: Context containing information about the repository.

        Returns:
            Whether the repository matches.

        Changes:
            - 0.24.0: Parameter `ctx` replaces parameter `repo`.
            - 0.25.0: Renamed from `match` to `filter`.
        """
        raise NotImplementedError("class does not implement Base.filter()")

    def match(self, ctx: Context) -> bool:
        """Determine if a Task applies to a repository.

        Args:
            ctx: Context containing information about the repository.

        Returns:
            Whether the repository matches.

        Deprecated:
            Use `filter()` instead.
        """
        return self.filter(ctx)


class FileExists(Base):
    """FileExists matches if the file exists in a repository.

    The code checks for the existence of a file by calling the API of the Source. This
    prevents useless checkouts of repositories and saves bandwidth.

    Args:
        path: Path to the file, relative to the root of the repository. Supports a
              wildcard in the name of the file, e.g. `dir/*.json`.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import FileExists

        with Task("example") as task:
            task.add_filter(FileExists("pyproject.toml"))
        ```
    """

    def __init__(self, path: str):
        self.path = path

    def __repr__(self):
        return f"FileExists(path={self.path})"

    def filter(self, ctx: Context) -> bool:
        return ctx.repo.has_file(self.path)


class LineInFile(Base):
    """LineInFile matches if a line in a file of a repository matches a regular
    expression.

    It downloads the file from the repository without checking out the whole repository.

    Args:
        path: Path of the file to check.
        search: Regular expression to test against each line in the file.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import LineInFile

        with Task("example") as task:
            task.add_filter(LineInFile(path=".gitignore", search="^\\.vscode?"))
        ```
    """

    def __init__(self, path: str, search: str):
        self.path = path
        self._search = search

        self.regex = re.compile(search)

    def __repr__(self):
        return f"LineInFile(path={self.path}, search={self._search})"

    def filter(self, ctx: Context) -> bool:
        try:
            content = ctx.repo.get_file(self.path)
            for line in content.readlines():
                if self.regex.match(line) is not None:
                    return True

            return False
        except FileNotFoundError:
            return False


class RepoName(Base):
    """RepoName matches if the name of a repository matches a regular expression.

    Args:
        search: Regular expression to test against names of repositories.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import RepoName

        with Task("example") as task:
            task.add_filter(RepoName("github.com/wndhydrnt/.*"))
        ```
    """

    def __init__(self, search: str):
        self._search = search
        self.regex = re.compile(search)

    def __repr__(self):
        return f"RepoName(search={self._search})"

    def filter(self, ctx: Context) -> bool:
        if self.regex.match(str(ctx.repo)) is None:
            return False

        return True


class Or(Base):
    """Or wraps multiple other filters. It matches if one of those filters matches.

    Args:
        args: One or more other filters.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import FileExists, Or

        with Task("example") as task:
            task.add_filter(
                Or(FileExists("pyproject.toml"), FileExists("requirements.txt"))
            )
        ```
    """

    def __init__(self, *args: Filter):
        if len(args) < 1:
            raise RuntimeError("Filter Or expects at least one argument")

        self.filters: tuple[Filter, ...] = args

    def __repr__(self) -> str:
        filters_repr: list[str] = []
        for m in self.filters:
            filters_repr.append(str(m))

        return f'Or(filters=[{", ".join(filters_repr)}])'

    def filter(self, ctx: Context) -> bool:
        for m in self.filters:
            if m(ctx) is True:
                return True

        return False


class And(Base):
    """And wraps multiple other filters. It matches if all of those filters match.

    Args:
        args: One or more filters.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import And, FileExists

        with Task("example") as task:
            task.add_filter(
                And(FileExists("pyproject.toml"), FileExists("poetry.lock"))
            )
        ```
    """

    def __init__(self, *args: Filter):
        if len(args) < 1:
            raise RuntimeError("Filter And expects at least one argument")

        self.filters: tuple[Filter, ...] = args

    def __repr__(self) -> str:
        filters_repr: list[str] = []
        for m in self.filters:
            filters_repr.append(str(m))

        return f'And(filters=[{", ".join(filters_repr)}])'

    def filter(self, ctx: Context) -> bool:
        for m in self.filters:
            if m(ctx) is False:
                return False

        return True


class Not(Base):
    """Not wraps a filter and negates its match result.

    Args:
        f: The filter to wrap.

    Example:
        ```python
        from rcmt import Task
        from rcmt.filter import FileExists, Not

        with Task("example") as task:
            task.add_filter(Not(FileExists("pyproject.toml")))
        ```
    """

    def __init__(self, f: Filter):
        self.f = f

    def __repr__(self):
        return f"Not(filter={str(self.f)})"

    def filter(self, ctx: Context) -> bool:
        return not self.f(ctx)
