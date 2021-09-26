import re

from rcmt import source


class Base:
    def match(self, repo: source.Repository) -> bool:
        raise NotImplementedError("class does not implement Base.match()")


class FileExists(Base):
    def __init__(self, path: str):
        self.path = path

    def match(self, repo: source.Repository) -> bool:
        return repo.has_file(self.path)


class RepoName(Base):
    def __init__(self, search: str):
        self.regex = re.compile(search)

    def match(self, repo: source.Repository) -> bool:
        if self.regex.match(str(repo)) is None:
            return False

        return True
