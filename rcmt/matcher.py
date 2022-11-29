import re

from rcmt import source


class Base:
    """
    Base class that describes the methods of a Matcher.
    """

    def match(self, repo: source.Repository) -> bool:
        """
        Indicates if a repository matches.

        :param repo: Repository to check.
        :return:
        """
        raise NotImplementedError("class does not implement Base.match()")


class FileExists(Base):
    """
    FileExists matches if the file exists in a repository.

    The code checks for the existence of a file by calling the API of the Source. This
    prevents useless checkouts of repositories and saves bandwidth.

    :param path: Path to the file, relative to the root of the repository.
                 Supports a wildcard in the name of the file, e.g. ``dir/*.json``.
    """

    def __init__(self, path: str):
        self.path = path

    def match(self, repo: source.Repository) -> bool:
        return repo.has_file(self.path)


class LineInFile(Base):
    """
    LineInFile matches if a line in a file of a repository matches a regular expression.

    It downloads the file from the repository without checking out the whole repository.

    :param path: Path of the file to check.
    :param search: Regular expression to test against each line in the file.

    .. versionadded:: 0.8.0
    """

    def __init__(self, path: str, search: str):
        self.path = path
        self.regex = re.compile(search)

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
    """
    RepoName matches if the name of a repository matches a regular expression.

    :param search: Regular expression to test against names of repositories.
    """

    def __init__(self, search: str):
        self.regex = re.compile(search)

    def match(self, repo: source.Repository) -> bool:
        if self.regex.match(str(repo)) is None:
            return False

        return True


class Or(Base):
    """
    Or wraps multiple other matchers. It matches if one of those matchers matches.

    :param args: One or more other matchers.

    .. versionadded:: 0.9.0
    """

    def __init__(self, *args: Base):
        if len(args) < 1:
            raise RuntimeError("Matcher Or expects at least one argument")

        self.matchers: tuple[Base, ...] = args

    def match(self, repo: source.Repository) -> bool:
        for m in self.matchers:
            if m.match(repo) is True:
                return True

        return False


class And(Base):
    """
    And wraps multiple other matchers. It matches if all of those matchers match.

    :param args: One or more matchers.

    .. versionadded:: 0.14.0
    """

    def __init__(self, *args: Base):
        if len(args) < 1:
            raise RuntimeError("Matcher And expects at least one argument")

        self.matchers: tuple[Base, ...] = args

    def match(self, repo: source.Repository) -> bool:
        for m in self.matchers:
            if m.match(repo) is False:
                return False

        return True


class Not(Base):
    """
    Not wraps a matcher and negates its match result.

    :param matcher: The matcher to wrap.

    .. versionadded:: 0.14.0
    """

    def __init__(self, matcher: Base):
        self.matcher: Base = matcher

    def match(self, repo: source.Repository) -> bool:
        return not self.matcher.match(repo)
