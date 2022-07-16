import datetime
import unittest
import unittest.mock
from typing import Any, Union

from rcmt import config, encoding, git, package, rcmt, source
from rcmt.config import Config
from rcmt.matcher import RepoName
from rcmt.package import action
from rcmt.rcmt import Options, RepoRun, execute_local
from rcmt.run import Run


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

    def find_pull_request(self, branch: str) -> Union[Any, None]:
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


def create_git_mock(
    branch_name: str, checkout_dir: str, needs_push: bool, has_changes_base: bool = True
):
    m = unittest.mock.Mock(spec=git.Git)
    m.branch_name = branch_name
    m.has_changes.return_value = needs_push
    m.has_changes_base.return_value = has_changes_base
    m.needs_push.return_value = needs_push
    m.prepare.return_value = checkout_dir
    return m


class RunTest(unittest.TestCase):
    def test_no_changes(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False)
        runner = RepoRun(git_mock, opts)
        run = Run(name="testrun")
        run.add_matcher(RepoName("local"))
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = None

        runner.execute(run, [pkg], repo_mock)

        action_mock.apply.assert_called_once_with(
            "/unit/test",
            {
                "repo_name": "myrepo",
                "repo_project": "myproject",
                "repo_source": "githost.com",
            },
        )
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_new_changes(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True)
        runner = RepoRun(git_mock, opts)
        run = Run(commit_msg="Custom commit", name="testrun")
        run.add_matcher(RepoName("local"))
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = None

        runner.execute(run, [pkg], repo_mock)

        git_mock.commit_changes.assert_called_once_with("/unit/test", "Custom commit")
        action_mock.apply.assert_called_once_with(
            "/unit/test",
            {
                "repo_name": "myrepo",
                "repo_project": "myproject",
                "repo_source": "githost.com",
            },
        )
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_called_once_with("/unit/test")
        expected_pr = source.PullRequest(
            run.auto_merge,
            run.merge_once,
            run.name,
            cfg.pr_title_prefix,
            "apply matcher testrun",
            cfg.pr_title_suffix,
        )
        repo_mock.create_pull_request.assert_called_once_with("rcmt", expected_pr)
        repo_mock.merge_pull_request.assert_not_called()

    def test_auto_merge_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False)
        runner = RepoRun(git_mock, opts)
        run = Run(
            auto_merge=True,
            auto_merge_after=datetime.timedelta(hours=12),
            name="testmatch",
        )
        run.add_matcher(RepoName("local"))
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.has_successful_pr_build.return_value = True
        repo_mock.is_pr_closed.return_value = False
        repo_mock.is_pr_open.return_value = True
        repo_mock.pr_created_at.return_value = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )

        runner.execute(run, [pkg], repo_mock)

        action_mock.apply.assert_called_once_with(
            "/unit/test",
            {
                "repo_name": "myrepo",
                "repo_project": "myproject",
                "repo_source": "githost.com",
            },
        )
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.has_successful_pr_build.assert_called_once_with("someid")
        repo_mock.merge_pull_request.assert_called_once_with("someid")

    def test_no_merge_closed_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True)
        runner = RepoRun(git_mock, opts)
        run = Run(name="testmatch")
        run.add_matcher(RepoName("local"))
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_closed.return_value = True

        runner.execute(run, [pkg], repo_mock)

        action_mock.apply.assert_not_called()
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.is_pr_closed.assert_called_once_with("someid")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_no_new_pr_if_merge_once_true(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True)
        runner = RepoRun(git_mock, opts)
        run = Run(name="testmatch", merge_once=True)
        run.add_matcher(RepoName("local"))
        pkg = package.Package("testpackage")
        action_mock = unittest.mock.Mock(spec=action.Action)
        pkg.actions.append(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = True

        runner.execute(run, [pkg], repo_mock)

        action_mock.apply.assert_not_called()
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.is_pr_merged.assert_called_once_with("someid")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_close_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False)
        run = Run(name="testmatch")
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True

        runner = RepoRun(git_mock, opts)
        runner.execute(run, [], repo_mock)

        repo_mock.close_pull_request.assert_called_once_with(
            "Everything up-to-date. Closing.", "someid"
        )
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()


class LocalTest(unittest.TestCase):
    @unittest.mock.patch("rcmt.run.read")
    def test_execute_local(self, run_read_mock):
        opts = Options(cfg=Config())
        opts.run_paths = ["/tmp/run.py"]
        opts.encoding_registry = encoding.Registry()
        run = Run(name="local")
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        run_read_mock.return_value = run

        execute_local("/tmp/repository", "github.com", "wndhydrnt", "rcmt", opts)

        run_read_mock.assert_called_with("/tmp/run.py")
        action_mock.apply.assert_called_once_with(
            "/tmp/repository",
            {
                "repo_source": "github.com",
                "repo_project": "wndhydrnt",
                "repo_name": "rcmt",
            },
        )
