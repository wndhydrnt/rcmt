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
from rcmt.git import BranchModifiedError
from rcmt.rcmt import (
    TEMPLATE_BRANCH_MODIFIED,
    Options,
    RepoRun,
    RunResult,
    execute,
    execute_task,
)
from rcmt.source import Base
from rcmt.task import Task, TaskWrapper, registry


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
        git_mock = create_git_mock("rcmt", "/tmp", False, False)
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.name = "testrun"
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = None
        ctx = context.Context(repo_mock)

        result = runner.execute(ctx=ctx, matcher=task)

        self.assertEqual(RunResult.NO_CHANGES, result)
        task.apply.assert_called_once_with(ctx=ctx)
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_new_changes(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", True, True)
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.commit_msg = "Custom commit"
        task.name = "testrun"
        task.on_pr_created = unittest.mock.Mock(return_value=None)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.is_pr_open.return_value = False
        repo_mock.find_pull_request.return_value = None
        ctx = context.Context(repo_mock)

        result = runner.execute(ctx=ctx, matcher=task)

        self.assertEqual(RunResult.PR_CREATED, result)
        git_mock.commit_changes.assert_called_once_with("/tmp", "Custom commit")
        task.apply.assert_called_once_with(ctx=ctx)
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_called_once_with("/tmp")
        expected_pr = source.PullRequest(
            task.auto_merge,
            task.merge_once,
            task.name,
            cfg.pr_title_prefix,
            "apply task testrun",
            cfg.pr_title_suffix,
        )
        repo_mock.create_pull_request.assert_called_once_with("rcmt", expected_pr)
        repo_mock.merge_pull_request.assert_not_called()
        task.on_pr_created.assert_called_once_with(ctx=ctx)

    def test_auto_merge_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False)
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.auto_merge = True
        task.auto_merge_after = datetime.timedelta(hours=12)
        task.name = "testmatch"
        task.on_pr_merged = unittest.mock.Mock(return_value=None)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.has_successful_pr_build.return_value = True
        repo_mock.is_pr_closed.return_value = False
        repo_mock.is_pr_open.return_value = True
        repo_mock.pr_created_at.return_value = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
        ctx = context.Context(repo_mock)

        result = runner.execute(ctx=ctx, matcher=task)

        self.assertEqual(RunResult.PR_MERGED, result)
        task.apply.assert_called_once_with(ctx=ctx)
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.has_successful_pr_build.assert_called_once_with("someid")
        repo_mock.merge_pull_request.assert_called_once_with("someid")
        task.on_pr_merged.assert_called_once_with(ctx=ctx)

    def test_no_merge_closed_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", True, True)
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.merge_once = True
        task.name = "testmatch"
        task.apply = unittest.mock.Mock(return_value=None)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_closed.return_value = True

        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(RunResult.PR_CLOSED_BEFORE, result)
        task.apply.assert_not_called()
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
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.merge_once = True
        task.name = "testmatch"
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.is_pr_merged.return_value = True

        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(RunResult.PR_MERGED_BEFORE, result)
        task.apply.assert_not_called()
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        repo_mock.is_pr_merged.assert_called_once_with("someid")
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_close_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False, False)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.name = "testmatch"
        task.on_pr_closed = unittest.mock.Mock(return_value=None)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True
        ctx = context.Context(repo_mock)

        runner = RepoRun(git_mock, opts)
        result = runner.execute(ctx=ctx, matcher=task)

        self.assertEqual(RunResult.PR_CLOSED, result)
        repo_mock.close_pull_request.assert_called_once_with(
            "Everything up-to-date. Closing.", "someid"
        )
        repo_mock.delete_branch.assert_called_once_with("someid")
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()
        task.on_pr_closed.assert_called_once_with(ctx=ctx)

    def test_no_changes_no_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False, False)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.name = "testmatch"
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = None

        runner = RepoRun(git_mock, opts)
        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(RunResult.NO_CHANGES, result)
        repo_mock.is_pr_open.assert_not_called()
        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()

    def test_update_pull_request(self):
        task = Task()
        task.name = "testmatch"
        task.apply = lambda ctx: None

        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False, True)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True

        runner = RepoRun(git_mock, opts)
        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(RunResult.PR_OPEN, result)
        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()
        pr_data = source.PullRequest(
            False,
            False,
            "testmatch",
            cfg.pr_title_prefix,
            "apply task testmatch",
            cfg.pr_title_suffix,
        )
        repo_mock.update_pull_request.assert_called_once_with("someid", pr_data)

    def test_cannot_merge_pull_request(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False, True)
        task = Task()
        task.auto_merge = True
        task.name = "testmatch"
        task.apply = lambda ctx: None
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True
        repo_mock.can_merge_pull_request.return_value = False

        runner = RepoRun(git_mock, opts)
        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(RunResult.CONFLICT, result)
        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_not_called()
        repo_mock.update_pull_request.assert_not_called()
        repo_mock.can_merge_pull_request.assert_called_once_with("someid")

    def test_does_not_delete_branch_if_disabled(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False, True)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.auto_merge = True
        task.delete_branch_after_merge = False
        task.name = "testmatch"
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.is_pr_merged.return_value = False
        repo_mock.is_pr_open.return_value = True
        repo_mock.can_merge_pull_request.return_value = True

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=task)

        repo_mock.close_pull_request.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()
        repo_mock.merge_pull_request.assert_called_once()
        repo_mock.update_pull_request.assert_not_called()
        repo_mock.can_merge_pull_request.assert_called_once()
        repo_mock.delete_branch.assert_not_called()

    def test_recreate_pr_if_closed(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", True, True)
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.commit_msg = "Custom commit"
        task.name = "testrun"
        task.apply = unittest.mock.Mock(return_value=None)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.is_pr_closed.return_value = True
        ctx = context.Context(repo_mock)

        result = runner.execute(ctx=ctx, matcher=task)

        self.assertEqual(RunResult.PR_CREATED, result)
        git_mock.commit_changes.assert_called_once_with("/tmp", "Custom commit")
        task.apply.assert_called_once_with(ctx=ctx)
        repo_mock.find_pull_request.assert_called_once_with("rcmt")
        git_mock.push.assert_called_once_with("/tmp")
        repo_mock.is_pr_closed.assert_has_calls([call("someid"), call("someid")])
        expected_pr = source.PullRequest(
            task.auto_merge,
            task.merge_once,
            task.name,
            cfg.pr_title_prefix,
            "apply task testrun",
            cfg.pr_title_suffix,
        )
        repo_mock.create_pull_request.assert_called_once_with("rcmt", expected_pr)
        repo_mock.merge_pull_request.assert_not_called()

    def test_no_pr_on_change_of_base_branch_and_no_open_pr(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False)
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.auto_merge = True
        task.auto_merge_after = datetime.timedelta(hours=12)
        task.name = "testmatch"
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = ""
        repo_mock.has_successful_pr_build.return_value = True
        repo_mock.is_pr_closed.return_value = False
        repo_mock.is_pr_merged.return_value = True
        repo_mock.is_pr_open.return_value = False
        repo_mock.pr_created_at.return_value = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        )

        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(RunResult.NO_CHANGES, result)
        git_mock.push.assert_not_called()
        repo_mock.create_pull_request.assert_not_called()

    @unittest.mock.patch("shutil.rmtree")
    def test_git_error(self, rmtree):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False)
        git_mock.prepare.side_effect = [
            GitCommandError(command=["git", "pull"]),
            ("/tmp", False),
        ]
        runner = RepoRun(git_mock, opts)
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.name = "testrun"
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = None

        runner.execute(ctx=context.Context(repo_mock), matcher=task)

        rmtree.assert_called_once_with("/tmp")
        git_mock.prepare.assert_has_calls(
            [
                call(force_rebase=False, repo=repo_mock),
                call(force_rebase=False, repo=repo_mock),
            ]
        )

    def test_branch_modified(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/unit/test", False, False)
        git_mock.prepare.side_effect = BranchModifiedError(["abc", "def"])
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.base_branch = "main"
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = "some body"
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.name = "testrun"

        runner = RepoRun(git_mock, opts)
        result = runner.execute(ctx=context.Context(repo_mock), matcher=task)

        self.assertEqual(result.BRANCH_MODIFIED, result)
        body = TEMPLATE_BRANCH_MODIFIED.render(
            checksums=["abc", "def"], default_branch="main"
        )
        repo_mock.create_pr_comment_with_identifier.assert_called_once_with(
            body=body, identifier="branch-modified", pr="someid"
        )
        repo_mock.get_pr_body.assert_called_once_with("someid")

    def test_delete_comment_on_force_rebase(self):
        cfg = config.Config()
        opts = Options(cfg)
        git_mock = create_git_mock("rcmt", "/tmp", False, False)
        repo_mock = unittest.mock.Mock(spec=source.Repository)
        repo_mock.name = "myrepo"
        repo_mock.project = "myproject"
        repo_mock.source = "githost.com"
        repo_mock.find_pull_request.return_value = "someid"
        repo_mock.get_pr_body.return_value = (
            "header\n[x] If you want to rebase this PR\nfooter"
        )
        task = Task()
        task.apply = unittest.mock.Mock(return_value=None)
        task.name = "testrun"

        runner = RepoRun(git_mock, opts)
        runner.execute(ctx=context.Context(repo_mock), matcher=task)

        repo_mock.delete_pr_comment_with_identifier.assert_called_once_with(
            identifier="branch-modified", pr="someid"
        )
        repo_mock.get_pr_body.assert_called_once_with("someid")


class ExecuteTaskTest(unittest.TestCase):
    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__successful(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        task = unittest.mock.Mock(spec=Task)
        task.change_limit = None
        task.name = "test"
        task.filter.return_value = True
        task_wrapper = TaskWrapper(t=task)
        repository = unittest.mock.Mock(spec=source.Repository)
        repository.name = "rcmt"
        repository.project = "wndhydrnt"
        repository.source = "github.test"
        opts = Options(cfg=Config())

        result = execute_task(task_wrapper=task_wrapper, repo=repository, opts=opts)

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
        task.change_limit = None
        task.filter.return_value = False
        task.name = "test"
        repository = unittest.mock.Mock(spec=source.Repository)
        opts = Options(cfg=Config())

        result = execute_task(
            task_wrapper=TaskWrapper(t=task), repo=repository, opts=opts
        )

        self.assertTrue(result)
        repo_run.execute.assert_not_called()

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__execute_exception(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run.execute.side_effect = RuntimeError
        repo_run_class.return_value = repo_run
        task = unittest.mock.Mock(spec=Task)
        task.filter.return_value = True
        task.name = "test"
        repository = unittest.mock.Mock(spec=source.Repository)
        opts = Options(cfg=Config())

        result = execute_task(
            task_wrapper=TaskWrapper(t=task), repo=repository, opts=opts
        )

        self.assertFalse(result)

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__filter_exception(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        task = unittest.mock.Mock(spec=Task)
        task.filter.side_effect = RuntimeError
        task.name = "test"
        wrapper = TaskWrapper(t=task)
        repository = unittest.mock.Mock(spec=source.Repository)
        opts = Options(cfg=Config())

        result = execute_task(task_wrapper=wrapper, repo=repository, opts=opts)

        self.assertFalse(result)

    @unittest.mock.patch("rcmt.rcmt.RepoRun")
    def test_execute_run__max_changes_reached(self, repo_run_class):
        repo_run = unittest.mock.Mock(spec=RepoRun)
        repo_run_class.return_value = repo_run
        repo_run.execute.return_value = RunResult.PR_CREATED
        task = unittest.mock.Mock(spec=Task)
        task.change_limit = 1
        task.name = "unittest"
        task.filter.return_value = True
        task_wrapper = TaskWrapper(t=task)
        repository_one = unittest.mock.Mock(spec=source.Repository)
        repository_one.name = "one"
        repository_one.project = "repository"
        repository_one.source = "github.test"
        repository_two = unittest.mock.Mock(spec=source.Repository)
        repository_two.name = "two"
        repository_two.project = "repository"
        repository_two.source = "github.test"
        opts = Options(cfg=Config())

        result_one = execute_task(
            task_wrapper=task_wrapper, repo=repository_one, opts=opts
        )
        result_two = execute_task(
            task_wrapper=task_wrapper, repo=repository_two, opts=opts
        )

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
            "9263296cd50d42b5fa23855f68824528",
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
            TaskWrapper,
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
            name="unit-test", checksum="9263296cd50d42b5fa23855f68824528"
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
            name="unit-test", checksum="9263296cd50d42b5fa23855f68824528"
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
            TaskWrapper,
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
            name="unit-test", checksum="9263296cd50d42b5fa23855f68824528"
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
            TaskWrapper,
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
            "d9c442b7ca9ce501b8b45c213d821747",
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
            "9263296cd50d42b5fa23855f68824528",
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
            TaskWrapper,
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
            "9263296cd50d42b5fa23855f68824528",
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
