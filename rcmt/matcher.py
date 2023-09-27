import re

from rcmt import source
from rcmt.typing import Matcher


class Base:
    """Base class that describes the methods of a Matcher."""

    def __call__(self, repo: source.Repository) -> bool:
        return self.match(repo)

    def __repr__(self) -> str:
        args: list[str] = []
        for k, v in self.__dict__.items():
            if k.startswith("_") is True:
                continue

            args.append(f"{k}={v}")

        return f'{self.__class__.__name__}({", ".join(args)})'

    def match(self, repo: source.Repository) -> bool:
        """Indicates if a repository matches.

        Args:
            repo: Repository to check.

        Returns:
            Whether the repository matches.
        """
        raise NotImplementedError("class does not implement Base.match()")


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
        from rcmt.matcher import FileExists

        with Task("example") as task:
            task.add_matcher(FileExists("pyproject.toml"))
        ```
    """

    def __init__(self, path: str):
        self.path = path

    def __repr__(self):
        return f"FileExists(path={self.path})"

    def match(self, repo: source.Repository) -> bool:
        return repo.has_file(self.path)


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
        from rcmt.matcher import LineInFile

        with Task("example") as task:
            task.add_matcher(LineInFile(path=".gitignore", search="^\\.vscode?"))
        ```
    """

    def __init__(self, path: str, search: str):
        self.path = path
        self._search = search

        self.regex = re.compile(search)

    def __repr__(self):
        return f"LineInFile(path={self.path}, search={self._search})"

    def match(self, repo: source.Repository) -> bool:
        try:
            content = repo.get_file(self.path)
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
        from rcmt.matcher import RepoName

        with Task("example") as task:
            task.add_matcher(RepoName("github.com/wndhydrnt/.*"))
        ```
    """

    def __init__(self, search: str):
        self._search = search
        self.regex = re.compile(search)

    def __repr__(self):
        return f"RepoName(search={self._search})"

    def match(self, repo: source.Repository) -> bool:
        if self.regex.match(str(repo)) is None:
            return False

        return True


class Or(Base):
    """Or wraps multiple other matchers. It matches if one of those matchers matches.

    Args:
        args: One or more other matchers.

    Example:
        ```python
        from rcmt import Task
        from rcmt.matcher import FileExists, Or

        with Task("example") as task:
            task.add_matcher(
                Or(FileExists("pyproject.toml"), FileExists("requirements.txt"))
            )
        ```
    """

    def __init__(self, *args: Matcher):
        if len(args) < 1:
            raise RuntimeError("Matcher Or expects at least one argument")

        self.matchers: tuple[Matcher, ...] = args

    def __repr__(self) -> str:
        matchers_repr: list[str] = []
        for m in self.matchers:
            matchers_repr.append(str(m))

        return f'Or(matchers=[{", ".join(matchers_repr)}])'

    def match(self, repo: source.Repository) -> bool:
        for m in self.matchers:
            if m(repo) is True:
                return True

        return False


class And(Base):
    """And wraps multiple other matchers. It matches if all of those matchers match.

    Args:
        args: One or more matchers.

    Example:
        ```python
        from rcmt import Task
        from rcmt.matcher import And, FileExists

        with Task("example") as task:
            task.add_matcher(
                And(FileExists("pyproject.toml"), FileExists("poetry.lock"))
            )
        ```
    """

    def __init__(self, *args: Matcher):
        if len(args) < 1:
            raise RuntimeError("Matcher And expects at least one argument")

        self.matchers: tuple[Matcher, ...] = args

    def __repr__(self) -> str:
        matchers_repr: list[str] = []
        for m in self.matchers:
            matchers_repr.append(str(m))

        return f'And(matchers=[{", ".join(matchers_repr)}])'

    def match(self, repo: source.Repository) -> bool:
        for m in self.matchers:
            if m(repo) is False:
                return False

        return True


class Not(Base):
    """Not wraps a matcher and negates its match result.

    Args:
        matcher: The matcher to wrap.

    Example:
        ```python
        from rcmt import Task
        from rcmt.matcher import FileExists, Not

        with Task("example") as task:
            task.add_matcher(Not(FileExists("pyproject.toml")))
        ```
    """

    def __init__(self, matcher: Matcher):
        self.matcher = matcher

    def __repr__(self):
        return f"Not(matcher={str(self.matcher)})"

    def match(self, repo: source.Repository) -> bool:
        return not self.matcher(repo)
