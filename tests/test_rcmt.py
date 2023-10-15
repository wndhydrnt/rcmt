# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import unittest
import unittest.mock
from typing import Any, Union
from unittest.mock import call

from git.exc import GitCommandError
from sqlalchemy import select

from rcmt import action, config, context, database, git, source
from rcmt.config import Config
from rcmt.config import Database as DatabaseConfig
from rcmt.database import Database, Execution, Run
from rcmt.matcher import RepoName
from rcmt.rcmt import Options, RepoRun, RunResult, execute, execute_task
from rcmt.source import Base
from rcmt.task import Task, registry


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
    branch_name: str,
    checkout_dir: str,
    has_changes_local: bool,
    has_changes_origin: bool,
    has_changes_base: bool = True,
    has_conflict: bool = False,
):
    m = unittest.mock.Mock(spec=git.Git)
    m.branch_name = branch_name
    m.checkout_dir.return_value = checkout_dir
    m.has_changes_local.return_value = has_changes_local
    m.has_changes_origin.side_effect = [has_changes_base, has_changes_origin]
    m.prepare.return_value = (checkout_dir, has_conflict)
    return m


class RepoRunTest(unittest.TestCase):
    def test_no_changes(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False)
        runner = RepoRun(git_mock, opts)
        run = Task(name="testrun")
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = None

        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        action_mock.assert_called_once_with(
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
        git_mock = create_git_mock("rcmt", "/unit/test", True, True)
        runner = RepoRun(git_mock, opts)
        run = Task(commit_msg="Custom commit", name="testrun")
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.is_pr_open.return_value = False
        repo_mock.find_pull_request.return_value = None
        ctx = context.Context(repo_mock)

        runner.execute(ctx=ctx, matcher=run)

        git_mock.commit_changes.assert_called_once_with("/unit/test", "Custom commit")
        action_mock.assert_called_once_with(
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
        git_mock = create_git_mock("rcmt", "/unit/test", False, False)
        runner = RepoRun(git_mock, opts)
        run = Task(
            auto_merge=True,
            auto_merge_after=datetime.timedelta(hours=12),
            name="testmatch",
        )
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
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
        ctx = context.Context(repo_mock)

        runner.execute(ctx=ctx, matcher=run)

        action_mock.assert_called_once_with(
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
        git_mock = create_git_mock("rcmt", "/unit/test", True, True)
        runner = RepoRun(git_mock, opts)
        run = Task(name="testmatch", merge_once=True)
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_closed.return_value = True

        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        action_mock.apply.assert_not_called()
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.is_pr_closed.assert_called_once_with("someid")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_no_new_pr_if_merge_once_true(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True, True)
        runner = RepoRun(git_mock, opts)
        run = Task(name="testmatch", merge_once=True)
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = True

        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        action_mock.apply.assert_not_called()
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.is_pr_merged.assert_called_once_with("someid")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_close_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False, False)
        run = Task(name="testmatch")
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        repo_mock.close_pull_request.assert_called_once_with(
            "Everything up-to-date. Closing.", "someid"
        )
        repo_mock.delete_branch.assert_called_once_with("someid")
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_no_changes_no_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False, False)
        run = Task(name="testmatch")
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = None

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        repo_mock.is_pr_open.assert_not_called()
        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_update_pull_request(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False, True)
        run = Task(name="testmatch")
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()
        pr_data = source.PullRequest(
            False,
            False,
            "testmatch",
            cfg.pr_title_prefix,
            "apply matcher testmatch",
            cfg.pr_title_suffix,
        )
        repo_mock.update_pull_request.assert_called_once_with("someid", pr_data)

    def test_cannot_merge_pull_request(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False, True)
        run = Task(name="testmatch", auto_merge=True)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True
        repo_mock.can_merge_pull_request.return_value = False

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()
        repo_mock.update_pull_request.assert_not_called()
        repo_mock.can_merge_pull_request.assert_called_once_with("someid")

    def test_does_not_delete_branch_if_disabled(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False, True)
        run = Task(name="testmatch", auto_merge=True, delete_branch_after_merge=False)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True
        repo_mock.can_merge_pull_request.return_value = True

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_called_once()
        repo_mock.update_pull_request.assert_not_called()
        repo_mock.can_merge_pull_request.assert_called_once()
        repo_mock.delete_branch.assert_not_called()

    def test_recreate_pr_if_closed(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True, True)
        runner = RepoRun(git_mock, opts)
        run = Task(commit_msg="Custom commit", name="testrun")
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_closed.return_value = True

        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        git_mock.commit_changes.assert_called_once_with("/unit/test", "Custom commit")
        action_mock.assert_called_once_with(
            "/unit/test",
            {
                "repo_name": "myrepo",
                "repo_project": "myproject",
                "repo_source": "githost.com",
            },
        )
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_called_once_with("/unit/test")
        repo_mock.is_pr_closed.assert_has_calls([call("someid"), call("someid")])
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

    def test_no_pr_on_change_of_base_branch_and_no_open_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False)
        runner = RepoRun(git_mock, opts)
        run = Task(
            auto_merge=True,
            auto_merge_after=datetime.timedelta(hours=12),
            name="testmatch",
        )
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.has_successful_pr_build.return_value = True
        repo_mock.is_pr_closed.return_value = False
        repo_mock.is_pr_merged.return_value = True
        repo_mock.is_pr_open.return_value = False
        repo_mock.pr_created_at.return_value = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )

        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()

    @unittest.mock.patch("shutil.rmtree")
    def test_git_error(self, rmtree):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False)
        git_mock.prepare.side_effect = [
            GitCommandError(command=["git", "pull"]),
            ("/unit/test", False),
        ]
        runner = RepoRun(git_mock, opts)
        run = Task(name="testrun")
        run.add_matcher(RepoName("local"))
        action_mock = unittest.mock.Mock(spec=action.Action)
        run.add_action(action_mock)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = None

        runner.execute(ctx=context.Context(repo_mock), matcher=run)

        rmtree.assert_called_once_with("/unit/test")
        git_mock.prepare.assert_has_calls([call(repo_mock), call(repo_mock)])


class ExecuteTaskTest(unittest.TestCase):
    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__successful(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        task = unittest.mock.Mock(spec=Task)
        task.has_reached_change_limit.return_value = False
        task.match.return_value = True
        task.name = "test"
        task.change_limit = None
        task.changes_total = 0
        repository = unittest.mock.Mock(spec=source.Repository)
        repository.name = "rcmt"
        repository.project = "wndhydrnt"
        repository.source = "github.test"
        opts = Options(cfg=Config())

        result = execute_task(task_=task, repo=repository, opts=opts)

        self.assertTrue(result)
        repo_run.execute.assert_called_once()
        ctx = repo_run.execute.call_args.kwargs["ctx"]
        self.assertIsInstance(ctx, context.Context)
        self.assertDictEqual(
            {
                "repo_name": "rcmt",
                "repo_project": "wndhydrnt",
                "repo_source": "github.test",
            },
            ctx.get_template_data(),
        )
        task_call = repo_run.execute.call_args.kwargs["matcher"]
        self.assertEqual(task, task_call)

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__does_not_match(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        task = unittest.mock.Mock(spec=Task)
        task.has_reached_change_limit.return_value = False
        task.match.return_value = False
        task.name = "test"
        repository = unittest.mock.Mock(spec=source.Repository)
        opts = Options(cfg=Config())

        result = execute_task(task_=task, repo=repository, opts=opts)

        self.assertTrue(result)
        repo_run.execute.assert_not_called()

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__execute_exception(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run.execute.side_effect = RuntimeError
        repo_run_class.return_value = repo_run
        run = unittest.mock.Mock(spec=Task)
        run.match.return_value = True
        run.name = "test"
        repository = unittest.mock.Mock(spec=source.Repository)
        opts = Options(cfg=Config())

        result = execute_task(task_=run, repo=repository, opts=opts)

        self.assertFalse(result)

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__match_exception(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        run = unittest.mock.Mock(spec=Task)
        run.match.side_effect = RuntimeError
        run.name = "test"
        repository = unittest.mock.Mock(spec=source.Repository)
        opts = Options(cfg=Config())

        result = execute_task(task_=run, repo=repository, opts=opts)

        self.assertFalse(result)

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__max_changes_reached(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        repo_run.execute.return_value = RunResult.PR_CREATED
        task = Task(name="unittest", change_limit=1)

        def return_true(*args, **kwargs) -> bool:
            return True

        task.match = return_true
        repository_one = unittest.mock.Mock(spec=source.Repository)
        repository_one.name = "one"
        repository_one.project = "repository"
        repository_one.source = "github.test"
        repository_two = unittest.mock.Mock(spec=source.Repository)
        repository_two.name = "two"
        repository_two.project = "repository"
        repository_two.source = "github.test"
        opts = Options(cfg=Config())

        result_one = execute_task(task_=task, repo=repository_one, opts=opts)
        result_two = execute_task(task_=task, repo=repository_two, opts=opts)

        self.assertTrue(result_one)
        self.assertTrue(result_two)
        repo_run.execute.assert_called_once()
        ctx = repo_run.execute.call_args.kwargs["ctx"]
        self.assertIsInstance(ctx, context.Context)
        self.assertDictEqual(
            {
                "repo_name": "one",
                "repo_project": "repository",
                "repo_source": "github.test",
            },
            ctx.get_template_data(),
        )
        task_call = repo_run.execute.call_args.kwargs["matcher"]
        self.assertEqual(task, task_call)


class ExecuteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.db: Database = database.new_database(DatabaseConfig())
        registry.task_path = None
        registry.tasks = []

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__no_repositories(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        source_mock = unittest.mock.Mock(spec=Base)
        source_mock.list_repositories.return_value = []
        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.sources = {"mock": source_mock}
        new_database_mock.return_value = self.db

        result = execute(opts)

        self.assertTrue(result)
        run_db = self.db.get_or_create_task(name="unit-test")
        self.assertEqual(run_db.checksum, "")
        execution_db = self.db.get_last_execution()
        self.assertIsNotNone(execution_db)
        execute_task_mock.assert_not_called()

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__no_previous_execution(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = [repo_mock]

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.sources = {"mock": source_mock}

        execute_task_mock.return_value = True

        result = execute(opts)

        self.assertTrue(result, msg="Should be successful")
        run_db = self.db.get_or_create_task(name="unit-test")
        self.assertEqual(
            run_db.checksum,
            "e96d87b82e15adb13ef63d6559b7ce85",
            msg="Should write the checksum because the Run was successfully executed",
        )
        execution_db = self.db.get_last_execution()
        self.assertIsNotNone(execution_db, msg="Should write the last execution")
        self.assertEqual(
            execute_task_mock.call_count,
            1,
            "Should execute a Run only once because one repository has been returned",
        )
        self.assertIsInstance(
            execute_task_mock.call_args.args[0],
            Task,
            "Should pass the Run to 'execute_run'",
        )
        self.assertEqual(
            repo_mock,
            execute_task_mock.call_args.args[1],
            "Should pass the repositories to 'execute_run'",
        )
        self.assertEqual(
            opts,
            execute_task_mock.call_args.args[2],
            "Should pass the options to 'execute_run'",
        )

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__query_repositories_since_previous_execution(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        executed_at = datetime.datetime.fromtimestamp(2934000)
        execution = Execution()
        execution.executed_at = executed_at
        self.db.save_execution(execution)

        self.db.get_or_create_task(name="unit-test")
        self.db.update_task(
            name="unit-test", checksum="e96d87b82e15adb13ef63d6559b7ce85"
        )

        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = [repo_mock]
        source_mock.list_repositories_with_open_pull_requests.return_value = []

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.sources = {"mock": source_mock}

        execute_task_mock.return_value = True

        result = execute(opts)

        self.assertTrue(result, msg="Should be successful")
        source_mock.list_repositories.assert_called_once_with(since=executed_at)

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__query_repositories_with_open_pull_requests(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        executed_at = datetime.datetime.fromtimestamp(2934000)
        execution = Execution()
        execution.executed_at = executed_at
        self.db.save_execution(execution)

        self.db.get_or_create_task(name="unit-test")
        self.db.update_task(
            name="unit-test", checksum="e96d87b82e15adb13ef63d6559b7ce85"
        )

        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = []
        source_mock.list_repositories_with_open_pull_requests.return_value = [repo_mock]

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.sources = {"mock": source_mock}

        execute_task_mock.return_value = True

        result = execute(opts)

        self.assertTrue(result, msg="Should be successful")
        source_mock.list_repositories_with_open_pull_requests.assert_called_once_with()
        self.assertIsInstance(
            execute_task_mock.call_args.args[0],
            Task,
            "Should pass the Run to 'execute_run'",
        )
        self.assertEqual(
            repo_mock,
            execute_task_mock.call_args.args[1],
            "Should pass the repositories to 'execute_run'",
        )
        self.assertEqual(
            opts,
            execute_task_mock.call_args.args[2],
            "Should pass the options to 'execute_run'",
        )

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__deduplicate_repositories(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        executed_at = datetime.datetime.fromtimestamp(2934000)
        execution = Execution()
        execution.executed_at = executed_at
        self.db.save_execution(execution)

        self.db.get_or_create_task(name="unit-test")
        self.db.update_task(
            name="unit-test", checksum="e96d87b82e15adb13ef63d6559b7ce85"
        )

        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = [repo_mock]
        source_mock.list_repositories_with_open_pull_requests.return_value = [repo_mock]

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.sources = {"mock": source_mock}

        execute_task_mock.return_value = True

        result = execute(opts)

        self.assertTrue(result, msg="Should be successful")
        source_mock.list_repositories_with_open_pull_requests.assert_called_once_with()
        self.assertIsInstance(
            execute_task_mock.call_args.args[0],
            Task,
            "Should pass the Run to 'execute_run'",
        )
        self.assertEqual(
            repo_mock,
            execute_task_mock.call_args.args[1],
            "Should pass the repositories to 'execute_task'",
        )
        self.assertEqual(
            opts,
            execute_task_mock.call_args.args[2],
            "Should pass the options to 'execute_run'",
        )

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__indicate_a_failed_run(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = [repo_mock]

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.sources = {"mock": source_mock}

        execute_task_mock.return_value = False

        result = execute(opts)

        self.assertFalse(result, msg="Should be unsuccessful")
        execute_task_mock.assert_called_once()

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__run_disabled(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = [repo_mock]
        source_mock.list_repositories_with_open_pull_requests.return_value = []

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task_disabled.py"]
        opts.sources = {"mock": source_mock}

        result = execute(opts)

        self.assertTrue(result, msg="Should be successful")
        task_db = self.db.get_or_create_task(name="unit-test")
        self.assertEqual(
            task_db.checksum,
            "992c6a2a2b39dabbf200c93c80059718",
            msg="Should write the checksum of the Run if it has been disabled",
        )
        execute_task_mock.assert_not_called()

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__no_sources(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        opts = Options(Config())
        opts.sources = {}
        new_database_mock.return_value = self.db

        with self.assertRaises(RuntimeError) as ee:
            execute(opts)

        self.assertEqual(
            str(ee.exception),
            "No Source has been configured. Configure access credentials for GitHub or GitLab.",
        )

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__repository_from_opts(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.create_from_name.return_value = repo_mock

        opts = Options(Config())
        opts.task_paths = ["tests/fixtures/test_rcmt/ExecuteTest/task.py"]
        opts.repositories = ["github.com/wndhydrnt/unit-test"]
        opts.sources = {"mock": source_mock}

        execute_task_mock.return_value = True

        result = execute(opts)

        self.assertTrue(result, msg="Should be successful")
        source_mock.create_from_name.assert_called_once_with(
            name="github.com/wndhydrnt/unit-test"
        )
        source_mock.list_repositories.assert_not_called()
        run_db = self.db.get_or_create_task(name="unit-test")
        self.assertEqual(
            run_db.checksum,
            "e96d87b82e15adb13ef63d6559b7ce85",
            msg="Should write the checksum because the Run was successfully executed",
        )
        execution_db = self.db.get_last_execution()
        self.assertIsNotNone(execution_db, msg="Should write the last execution")
        self.assertEqual(
            execute_task_mock.call_count,
            1,
            "Should execute a Run only once because one repository has been returned",
        )
        self.assertIsInstance(
            execute_task_mock.call_args.args[0],
            Task,
            "Should pass the Run to 'execute_run'",
        )
        self.assertEqual(
            repo_mock,
            execute_task_mock.call_args.args[1],
            "Should pass the repositories to 'execute_run'",
        )
        self.assertEqual(
            opts,
            execute_task_mock.call_args.args[2],
            "Should pass the options to 'execute_run'",
        )

    @unittest.mock.patch("rcmt.database.new_database")
    @unittest.mock.patch("rcmt.rcmt.execute_task")
    def test_execute__task_exception(
        self,
        execute_task_mock: unittest.mock.MagicMock,
        new_database_mock: unittest.mock.MagicMock,
    ) -> None:
        new_database_mock.return_value = self.db
        source_mock = unittest.mock.Mock(spec=Base)
        repo_mock = RepositoryMock(
            name="unit-test", project="wndhydrnt", src="github.com", has_file=False
        )
        source_mock.list_repositories.return_value = [repo_mock]
        source_mock.list_repositories_with_open_pull_requests.return_value = []

        opts = Options(Config())
        opts.task_paths = [
            "tests/fixtures/test_rcmt/ExecuteTest/task.py",
            "tests/fixtures/test_rcmt/ExecuteTest/task_exception.py",
        ]
        opts.sources = {"mock": source_mock}

        result = execute(opts)

        self.assertFalse(
            result, msg="Should not be successful because one Task could not be read"
        )
        task_db = self.db.get_or_create_task(name="unit-test")
        self.assertEqual(
            task_db.checksum,
            "e96d87b82e15adb13ef63d6559b7ce85",
            msg="Should write the checksum of the working Task to the DB",
        )
        with self.db.session() as session, session.begin():
            stmt = select(Run).where(Run.name == "unit-test-exception")
            task_exception_db = session.scalars(stmt).first()

        self.assertIsNone(
            task_exception_db,
            "Should not write the checksum of the invalid Task to the DB",
        )

        self.assertEqual(
            execute_task_mock.call_count,
            1,
            "Should execute the Task that is valid",
        )
        self.assertEqual(
            execute_task_mock.call_args.args[0].name,
            "unit-test",
            "Should pass the Task to 'execute_run'",
        )
        self.assertEqual(
            repo_mock,
            execute_task_mock.call_args.args[1],
            "Should pass the repository to 'execute_task'",
        )
        self.assertEqual(
            opts,
            execute_task_mock.call_args.args[2],
            "Should pass the options to 'execute_task'",
        )
