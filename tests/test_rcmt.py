import unittest
from typing import Any, Union

from rcmt import config, rcmt, source


class RepositoryMock(source.Repository):
    def __init__(self, name: str, project: str, src: str):
        self._name = name
        self._project = project
        self._source = src

    @property
    def base_branch(self) -> str:
        return "main"

    @property
    def clone_url(self) -> str:
        return "clone_url"

    def create_pull_request(self, branch: str, pr: source.PullRequest) -> None:
        return None

    def find_open_pull_request(self, branch: str) -> Union[Any, None]:
        return None

    def has_successful_pr_build(self, identifier: Any) -> bool:
        return False

    def merge_pull_request(self, identifier: Any) -> None:
        return None

    @property
    def name(self) -> str:
        return self._name

    @property
    def project(self) -> str:
        return self._project

    @property
    def source(self) -> str:
        return self._source


class MatchRepositoriesTest(unittest.TestCase):
    def test_match_repositories(self):
        repositories = [
            RepositoryMock("rcmt", "wndhydrnt", "github.com"),
            RepositoryMock("rcmt-packages", "wndhydrnt", "github.com"),
            RepositoryMock("other", "wndhydrnt", "github.com"),
        ]

        match = config.Match(repository="github.com/wndhydrnt/rcmt")
        result = rcmt.match_repositories(repositories, match)
        self.assertEqual(2, len(result))
        self.assertEqual(result[0].name, "rcmt")
        self.assertEqual(result[1].name, "rcmt-packages")

        match = config.Match(repository="^github.com/wndhydrnt/rcmt$")
        result = rcmt.match_repositories(repositories, match)
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].name, "rcmt")
