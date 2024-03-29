# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import shutil
from enum import Enum
from typing import Any, Iterator, Optional

import jinja2
from git.exc import GitCommandError

import rcmt.log

from . import config, context, database, fs, git, metric, source, task

log = rcmt.log.get_logger(__name__)


TEMPLATE_BRANCH_MODIFIED = jinja2.Template(
    """:warning: **This pull request has been modified.**

This is a safety mechanism to prevent rcmt from accidentally overriding custom commits.

rcmt will not be able to resolve merge conflicts with `{{ default_branch }}` automatically.
It will not update this pull request or auto-merge it.

Check the box in the description of this PR to force a rebase. This will remove all commits not made by rcmt.

The commit(s) that modified the pull request:
{% for checksum in checksums %}
- {{ checksum }}
{% endfor %}
"""
)


class Options:
    def __init__(self, cfg: config.Config):
        self.config = cfg
        self.task_paths: list[str] = []
        self.repositories: list[str] = []
        self.sources: dict[str, source.Base] = {}


def can_merge_after(
    created_at: datetime.datetime, delay: Optional[datetime.timedelta]
) -> bool:
    if delay is None:
        return True

    passed = datetime.datetime.now(tz=datetime.timezone.utc) - created_at
    return passed >= delay


class RunResult(Enum):
    # PR could be merged but auto_merge_after setting prevents it
    AUTO_MERGE_TOO_EARLY = 1
    # Someone other than rcmt has pushed commits to the branch
    BRANCH_MODIFIED = 2
    # PR checks (approvals, tests etc.) have failed
    CHECKS_FAILED = 3
    # Conflict with default branch
    CONFLICT = 4
    # No modifications to any files
    NO_CHANGES = 5
    # PR created by the current Run
    PR_CREATED = 6
    # PR was closed during a previous Run
    PR_CLOSED_BEFORE = 7
    # PR closed by the current Run
    PR_CLOSED = 8
    # PR was merged during a previous Run
    PR_MERGED_BEFORE = 9
    # PR merged by the current Run
    PR_MERGED = 10
    # PR is open and the current run did not modify anything
    PR_OPEN = 11


class RepoRun:
    def __init__(self, g: git.Git, opts: Options):
        self.git = g
        self.opts = opts

    def execute(
        self,
        ctx: context.Context,
        matcher: task.Task,
    ) -> RunResult:
        repo = ctx.repo
        pr_identifier = repo.find_pull_request(self.git.branch_name)
        if (
            pr_identifier is not None
            and repo.is_pr_closed(pr_identifier) is True
            and matcher.merge_once is True
        ):
            log.info("Existing PR has been closed branch=%s", self.git.branch_name)
            return RunResult.PR_CLOSED_BEFORE

        if (
            pr_identifier is not None
            and repo.is_pr_merged(pr_identifier) is True
            and matcher.merge_once is True
        ):
            log.info("Existing PR has been merged branch=%s", self.git.branch_name)
            return RunResult.PR_MERGED_BEFORE

        if pr_identifier is not None and matcher.create_only is True:
            return RunResult.PR_OPEN

        force_rebase = self._has_rebase_checked(pr=pr_identifier, repo=repo)
        try:
            work_dir, has_conflict = self.git.prepare(
                force_rebase=force_rebase, repo=repo
            )
            if force_rebase is True:
                # It is likely that the branch was modified previously and a comment was
                # created to notify the user. Delete that comment.
                repo.delete_pr_comment_with_identifier(
                    identifier="branch-modified", pr=pr_identifier
                )

        except git.BranchModifiedError as e:
            log.warning("Branch contains commits not made by rcmt")
            if self.opts.config.dry_run is True:
                log.warning("DRY RUN: Not creating note on pull request")
            else:
                ctx.repo.create_pr_comment_with_identifier(
                    body=TEMPLATE_BRANCH_MODIFIED.render(
                        checksums=e.checksums, default_branch=repo.base_branch
                    ),
                    identifier="branch-modified",
                    pr=pr_identifier,
                )

            return RunResult.BRANCH_MODIFIED
        except GitCommandError as e:
            # Catch any error raised by the git client, delete the repository and
            # initialize it again
            log.warning(
                msg="generic git error detected - cloning repository again",
                exc_info=e,
            )
            checkout_dir = self.git.checkout_dir(repo)
            shutil.rmtree(checkout_dir)
            work_dir, has_conflict = self.git.prepare(
                force_rebase=force_rebase, repo=repo
            )

        with fs.in_checkout_dir(work_dir):
            matcher.apply(ctx=ctx)

        has_local_changes = self.git.has_changes_local(work_dir)
        if has_local_changes is True:
            self.git.commit_changes(work_dir, matcher.commit_msg)
        else:
            log.info("No changes after applying actions")

        if (
            self.git.has_changes_origin(branch=repo.base_branch, repo_dir=work_dir)
            is False
            and pr_identifier is not None
            and repo.is_pr_open(pr_identifier) is True
        ):
            if self.opts.config.dry_run:
                log.warning(
                    "DRY RUN: Closing pull request because base branch contains all changes"
                )
            else:
                log.info(
                    "Closing pull request because base branch contains all changes",
                )
                repo.close_pull_request(
                    "Everything up-to-date. Closing.", pr_identifier
                )
                log.info(
                    "Deleting source branch because base branch contains all changes branch=%s",
                    self.git.branch_name,
                )
                repo.delete_branch(pr_identifier)
                matcher.on_pr_closed(ctx=ctx)

            return RunResult.PR_CLOSED

        has_changes = (
            has_local_changes
            and self.git.has_changes_origin(
                branch=self.git.branch_name, repo_dir=work_dir
            )
        ) or has_conflict
        if has_changes is True:
            if self.opts.config.dry_run:
                log.warning("DRY RUN: Not pushing changes")
            else:
                log.debug("Pushing changes")
                self.git.push(work_dir)

        pr = source.PullRequest(
            matcher.auto_merge,
            matcher.merge_once,
            matcher.name,
            self.opts.config.pr_title_prefix,
            self.opts.config.pr_title_body.format(matcher_name=matcher.name),
            self.opts.config.pr_title_suffix,
            matcher.pr_body,
            matcher.pr_title,
            auto_merge_after=matcher.auto_merge_after,
            labels=matcher.labels,
            tpl_data=ctx.get_template_data(),
        )
        if has_changes is True and (
            pr_identifier is None
            or repo.is_pr_merged(pr_identifier) is True
            or repo.is_pr_closed(pr_identifier) is True
        ):
            if self.opts.config.dry_run:
                log.warning("DRY RUN: Not creating pull request")
            else:
                log.info("Create pull request")
                repo.create_pull_request(self.git.branch_name, pr)
                matcher.on_pr_created(ctx=ctx)

            return RunResult.PR_CREATED

        if (
            matcher.auto_merge is True
            and has_changes is False
            and pr_identifier is not None
            and repo.is_pr_open(pr_identifier) is True
        ):
            if not repo.has_successful_pr_build(pr_identifier):
                log.warning("Cannot merge because build of pull request failed")
                return RunResult.CHECKS_FAILED

            if not can_merge_after(
                repo.pr_created_at(pr_identifier), matcher.auto_merge_after
            ):
                log.info("Too early to merge pull request")
                return RunResult.AUTO_MERGE_TOO_EARLY

            if not repo.can_merge_pull_request(pr_identifier):
                log.warning("Cannot merge pull request")
                return RunResult.CONFLICT

            if self.opts.config.dry_run:
                log.warning("DRY RUN: Not merging pull request")
            else:
                log.info("Merge pull request")
                repo.merge_pull_request(pr_identifier)
                if matcher.delete_branch_after_merge:
                    log.info(
                        "Deleting source branch branch=%s",
                        self.git.branch_name,
                    )
                    repo.delete_branch(pr_identifier)
                    matcher.on_pr_merged(ctx=ctx)

            return RunResult.PR_MERGED

        if pr_identifier is not None and repo.is_pr_open(pr_identifier) is True:
            repo.update_pull_request(pr_identifier, pr)
            return RunResult.PR_OPEN

        return RunResult.NO_CHANGES

    @staticmethod
    def _has_rebase_checked(pr: Any, repo: source.Repository) -> bool:
        if pr is None:
            return False

        desc = repo.get_pr_body(pr)
        return "[x] If you want to rebase this PR" in desc


def execute(opts: Options) -> bool:
    if len(opts.sources) < 1:
        raise RuntimeError(
            "No Source has been configured. Configure access credentials for GitHub or GitLab."
        )

    metric.run_start_timestamp.set_to_current_time()
    db = database.new_database(opts.config.database)
    tasks, needs_all_repositories, reads_succeeded = read_tasks(
        db=db, task_paths=opts.task_paths
    )
    if len(opts.repositories) > 0:
        log.info("Reading repositories passed in from command-line")
        cli_repositories: list[source.Repository] = []
        for repository_name in opts.repositories:
            for s in opts.sources.values():
                repository = s.create_from_name(name=repository_name)
                if repository is not None:
                    cli_repositories.append(repository)

        repositories: Iterator[source.Repository] = (
            repository for repository in cli_repositories
        )

    else:
        execution = db.get_last_execution()
        if needs_all_repositories is True or execution.executed_at is None:
            since = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        else:
            since = execution.executed_at

        log.debug(
            "Searching for updated repositories since %s",
            str(since),
        )
        repositories = list_repositories(
            all_repositories=needs_all_repositories,
            since=since,
            sources=list(opts.sources.values()),
        )

    repository_count: int = 0
    success = reads_succeeded
    for repository in repositories:
        repository_count += 1
        for task_ in tasks:
            rcmt.log.clear_contextvars()
            rcmt.log.bind_contextvars(repository=repository.full_name, task=task_.name)
            task_success = execute_task(task_, repository, opts)
            rcmt.log.clear_contextvars()
            if task_success is False:
                task_.failure_count += 1
                success = False

    log.info("Finished processing of %d repositories", repository_count)
    metric.run_repositories_processed.set(repository_count)

    if repository_count > 0:
        for task_ in tasks:
            if task_.failure_count == 0:
                # Only update the checksum if the task did not fail.
                # Without an updated checksum, on the next run, rcmt ensures that all
                # repositories are visited by the task again.
                # This logic guarantees that, if a new task fails, it is able to visit
                # the failed repositories again.
                db.update_task(task_.name, task_.checksum)

    metric.run_error.set(0)
    if success is False:
        log.error("Errors during execution - check previous log messages")
        metric.run_error.set(1)

    ex = database.Execution()
    ex.executed_at = datetime.datetime.now(tz=datetime.timezone.utc)
    db.save_execution(ex)
    metric.run_finish_timestamp.set_to_current_time()
    metric.push(opts.config.pushgateway)
    return success


def execute_task(
    task_wrapper: task.TaskWrapper,
    repo: source.Repository,
    opts: Options,
) -> bool:
    gitc = git.Git(
        task_wrapper.branch(opts.config.git.branch_prefix),
        opts.config.git.clone_options,
        opts.config.git.data_dir,
        opts.config.git.user_name,
        opts.config.git.user_email,
    )
    runner = RepoRun(gitc, opts)
    success = True
    try:
        if task_wrapper.has_reached_change_limit():
            log.info(
                "Limit of changes reached for task limit=%d", task_wrapper.change_limit
            )
            return success

        ctx = context.Context(repo, custom_config=opts.config.custom)
        if task_wrapper.filter(ctx) is False:
            log.debug("Repository does not match task")
            return success

        log.info("Task matched repository")
        result: RunResult = runner.execute(ctx=ctx, matcher=task_wrapper.task)
        if result == RunResult.PR_CREATED or result == RunResult.PR_MERGED:
            task_wrapper.changes_total += 1

    except Exception as e:
        log.exception("Task failed", exc_info=e)
        success = False

    return success


def options_from_config(path: str) -> Options:
    cfg = config.read_config_from_file(path)
    return config_to_options(cfg)


def config_to_options(cfg: config.Config) -> Options:
    opts = Options(cfg)
    if cfg.github.access_token != "":
        source_github = source.Github(cfg.github.access_token, cfg.github.base_url)
        opts.sources["github"] = source_github

    if cfg.gitlab.private_token != "":
        source_gitlab = source.Gitlab(cfg.gitlab.url, cfg.gitlab.private_token)
        opts.sources["gitlab"] = source_gitlab

    return opts


def list_repositories(
    all_repositories: bool,
    since: datetime.datetime,
    sources: list[source.Base],
) -> Iterator[source.Repository]:
    known_repos: list[str] = []
    for s in sources:
        for repository in s.list_repositories(since=since):
            known_repos.append(str(repository))
            yield repository

        if all_repositories is False:
            log.debug("Listing repositories with open pull requests")
            for repository in s.list_repositories_with_open_pull_requests():
                if str(repository) in known_repos:
                    continue

                known_repos.append(str(repository))
                yield repository


def read_tasks(
    db: database.Database, task_paths: list[str]
) -> tuple[list[task.TaskWrapper], bool, bool]:
    tasks: list[task.TaskWrapper] = []
    needs_all_repositories: bool = False
    all_reads_succeed: bool = True
    for task_path in task_paths:
        try:
            task.read(task_path)
        except RuntimeError as e:
            log.exception(
                "Loading task from file failed file=%s", task_path, exc_info=e
            )
            all_reads_succeed = False
            continue

    for wrapper in task.registry.tasks:
        task_db = db.get_or_create_task(name=wrapper.name)
        if wrapper.task.enabled is False:
            db.update_task(wrapper.name, wrapper.checksum)
            log.info("Task disabled task=%s", wrapper.name)
            continue

        if wrapper.checksum != task_db.checksum:
            needs_all_repositories = True

        tasks.append(wrapper)

    return tasks, needs_all_repositories, all_reads_succeed
