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
    def __init__(self, path: str, regex: str):
        self.path = path
        self.regex = re.compile(regex)

    def match(self, repo: source.Repository) -> bool:
        try:
            content = repo.get_file(self.path)
            for line in content.readlines():
                if self.regex.search(line) is not None:
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
