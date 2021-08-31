import datetime
import unittest
import unittest.mock
from typing import Any, Union

from rcmt import action, config, git, package, rcmt, source
from rcmt.rcmt import Options, Run


class RepositoryMock(source.Repository):
    def __init__(self, name: str, project: str, src: str, has_file=True):
        self._has_file = has_file
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

    def has_file(self, path: str) -> bool:
        return self._has_file

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


def create_git_mock(branch_name: str, checkout_dir: str, needs_push: bool):
    m = unittest.mock.Mock(spec=git.Git)
    m.branch_name = branch_name
    m.has_changes.return_value = needs_push
    m.needs_push.return_value = needs_push
    m.prepare.return_value = checkout_dir
    return m


class RunTest(unittest.TestCase):
    def test_no_changes(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False)
        runner = Run(git_mock, opts)
        matcher = config.Matcher(
            match=config.Match(repository="local"), name="testmatch"
        )
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_open_pull_request.return_value = None

        runner.execute(matcher, [pkg], repo_mock)

        action_mock.apply.assert_called_once_with(
            "/unit/test", {"repo_name": "myrepo", "repo_project": "myproject"}
        )
        repo_mock.find_open_pull_request.assert_called_once_with("rcmt")
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_new_changes(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True)
        runner = Run(git_mock, opts)
        matcher = config.Matcher(
            match=config.Match(repository="local"), name="testmatch"
        )
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_open_pull_request.return_value = None

        runner.execute(matcher, [pkg], repo_mock)

        action_mock.apply.assert_called_once_with(
            "/unit/test", {"repo_name": "myrepo", "repo_project": "myproject"}
        )
        repo_mock.find_open_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_called_once_with("/unit/test")
        expected_pr = source.PullRequest(
            cfg.pr_title_prefix, "apply matcher testmatch", cfg.pr_title_suffix
        )
        expected_pr.add_package("testpackage")
        repo_mock.create_pull_request.assert_called_once_with("rcmt", expected_pr)
        repo_mock.merge_pull_request.assert_not_called()

    def test_auto_merge_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False)
        runner = Run(git_mock, opts)
        matcher = config.Matcher(
            auto_merge=True,
            auto_merge_after="PT12H",
            match=config.Match(repository="local"),
            name="testmatch",
        )
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_open_pull_request.return_value = "someid"
        repo_mock.has_successful_pr_build.return_value = True
        repo_mock.pr_created_at.return_value = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )

        runner.execute(matcher, [pkg], repo_mock)

        action_mock.apply.assert_called_once_with(
            "/unit/test", {"repo_name": "myrepo", "repo_project": "myproject"}
        )
        repo_mock.find_open_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.has_successful_pr_build.assert_called_once_with("someid")
        repo_mock.merge_pull_request.assert_called_once_with("someid")


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

        match = config.Match(
            paths=["pyproject.toml"], repository="^github.com/wndhydrnt/rcmt$"
        )
        result = rcmt.match_repositories(repositories, match)
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].name, "rcmt")

        match = config.Match(
            paths=["pyproject.toml"], repository="^github.com/wndhydrnt/rcmt$"
        )
        result = rcmt.match_repositories(
            [RepositoryMock("rcmt", "wndhydrnt", "github.com", has_file=False)], match
        )
        self.assertEqual(0, len(result))
