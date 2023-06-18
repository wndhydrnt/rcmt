import datetime
from enum import Enum
from typing import Optional

import structlog

from . import config, database, encoding, git, source, task

log: structlog.stdlib.BoundLogger = structlog.get_logger()


class Options:
    def __init__(self, cfg: config.Config):
        self.config = cfg
        self.encoding_registry: encoding.Registry = encoding.Registry()
        self.task_paths: list[str] = []
        self.sources: dict[str, source.Base] = {}


def can_merge_after(
    created_at: datetime.datetime, delay: Optional[datetime.timedelta]
) -> bool:
    if delay is None:
        return True

    passed = datetime.datetime.now() - created_at
    return passed >= delay


class RunResult(Enum):
    NO_CHANGES = 1
    PR_CREATED = 2
    PR_MERGED = 3


class RepoRun:
    def __init__(self, g: git.Git, opts: Options):
        self.git = g
        self.opts = opts

    def execute(self, matcher: task.Task, repo: source.Repository) -> RunResult:
        pr_identifier = repo.find_pull_request(self.git.branch_name)
        if (
            pr_identifier is not None
            and repo.is_pr_closed(pr_identifier) is True
            and matcher.merge_once is True
        ):
            log.info(
                "Existing PR has been closed",
                branch=self.git.branch_name,
                repo=str(repo),
            )
            return RunResult.NO_CHANGES

        if (
            pr_identifier is not None
            and repo.is_pr_merged(pr_identifier) is True
            and matcher.merge_once is True
        ):
            log.info(
                "Existing PR has been merged",
                branch=self.git.branch_name,
                repo=str(repo),
            )
            return RunResult.NO_CHANGES

        work_dir = self.git.prepare(repo)
        tpl_mapping = create_template_mapping(repo)
        apply_actions(repo, matcher, tpl_mapping, work_dir)
        has_changes = self.git.has_changes(work_dir)
        if has_changes is True:
            log.debug("Committing changes", repo=str(repo))
            self.git.commit_changes(work_dir, matcher.commit_msg)
        else:
            log.info("No changes after applying actions", repo=str(repo))

        if (
            self.git.has_changes_base(base_branch=repo.base_branch, repo_dir=work_dir)
            is False
            and pr_identifier is not None
            and repo.is_pr_open(pr_identifier) is True
        ):
            if self.opts.config.dry_run:
                log.warn(
                    "DRY RUN: Closing pull request because base branch contains all changes"
                )
            else:
                log.info(
                    "Closing pull request because base branch contains all changes",
                    repo=str(repo),
                )
                repo.close_pull_request(
                    "Everything up-to-date. Closing.", pr_identifier
                )
                log.info(
                    "Deleting source branch because base branch contains all changes",
                    branch=self.git.branch_name,
                    repo=str(repo),
                )
                repo.delete_branch(pr_identifier)

            return RunResult.NO_CHANGES

        if has_changes is True:
            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not pushing changes")
            else:
                log.debug("Pushing changes", repo=str(repo))
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
        )
        if has_changes is True and (
            pr_identifier is None
            or repo.is_pr_merged(pr_identifier) is True
            or repo.is_pr_closed(pr_identifier) is True
        ):
            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not creating pull request")
            else:
                log.info("Create pull request", repo=str(repo))
                repo.create_pull_request(self.git.branch_name, pr)

            return RunResult.PR_CREATED

        if (
            matcher.auto_merge is True
            and has_changes is False
            and pr_identifier is not None
            and repo.is_pr_open(pr_identifier) is True
        ):
            if not repo.has_successful_pr_build(pr_identifier):
                log.warn(
                    "Cannot merge because build of pull request failed", repo=str(repo)
                )
                return RunResult.NO_CHANGES

            if not can_merge_after(
                repo.pr_created_at(pr_identifier), matcher.auto_merge_after
            ):
                log.info("Too early to merge pull request", repo=str(repo))
                return RunResult.NO_CHANGES

            if not repo.can_merge_pull_request(pr_identifier):
                log.warn("Cannot merge pull request", repo=str(repo))
                return RunResult.NO_CHANGES

            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not merging pull request", repo=str(repo))
            else:
                log.info("Merge pull request", repo=str(repo))
                repo.merge_pull_request(pr_identifier)
                if matcher.delete_branch_after_merge:
                    log.info(
                        "Deleting source branch",
                        branch=self.git.branch_name,
                        repo=str(repo),
                    )
                    repo.delete_branch(pr_identifier)

            return RunResult.PR_MERGED

        if pr_identifier is not None and repo.is_pr_open(pr_identifier) is True:
            repo.update_pull_request(pr_identifier, pr)
            return RunResult.NO_CHANGES

        return RunResult.NO_CHANGES


def apply_actions(
    repo: source.Repository,
    task_: task.Task,
    tpl_mapping: dict,
    work_dir: str,
) -> None:
    for a in task_.actions:
        log.debug(
            "Applying action from task",
            action=a.__class__.__name__,
            task=task_.name,
            repo=str(repo),
        )
        a.apply(work_dir, tpl_mapping)


def execute(opts: Options) -> bool:
    if len(opts.sources) < 1:
        raise RuntimeError(
            "No Source has been configured. Configure access credentials for GitHub or GitLab."
        )

    db = database.new_database(opts.config.database)
    tasks: list[task.Task] = []
    needs_all_repositories = False
    for task_path in opts.task_paths:
        task_ = task.read(task_path)
        task_db = db.get_or_create_task(name=task_.name)
        if task_.enabled is False:
            db.update_task(task_.name, task_.checksum)
            log.info("Task disabled", task=task_.name)
            continue

        if task_.checksum != task_db.checksum:
            needs_all_repositories = True

        tasks.append(task_)

    execution = db.get_last_execution()
    if needs_all_repositories is True or execution.executed_at is None:
        since = datetime.datetime.fromtimestamp(0)
    else:
        since = execution.executed_at

    log.debug("Searching for updated repositories", since=str(since))
    repositories: list[source.Repository] = []
    for s in opts.sources.values():
        known_repos: list[str] = []
        for repository in s.list_repositories(since=since):
            known_repos.append(str(repository))
            repositories.append(repository)

        if needs_all_repositories is False:
            log.debug("Listing repositories with open pull requests")
            for repository in s.list_repositories_with_open_pull_requests():
                if str(repository) in known_repos:
                    continue

                known_repos.append(str(repository))
                repositories.append(repository)

    log.info("Repositories returned by sources", count=len(repositories))
    success = True
    if len(repositories) > 0:
        for task_ in tasks:
            task_success = execute_task(task_, repositories, opts)
            if task_success is True:
                db.update_task(task_.name, task_.checksum)
            else:
                success = False

    if success is False:
        log.error("Errors during execution - check previous log messages")

    ex = database.Execution()
    ex.executed_at = datetime.datetime.utcnow()
    db.save_execution(ex)
    return success


def execute_task(
    task_: task.Task,
    repos: list[source.Repository],
    opts: Options,
) -> bool:
    gitc = git.Git(
        task_.branch(opts.config.git.branch_prefix),
        opts.config.git.clone_options,
        opts.config.git.data_dir,
        opts.config.git.user_name,
        opts.config.git.user_email,
    )
    runner = RepoRun(gitc, opts)
    success = True
    changes_total: int = 0
    for repo in repos:
        try:
            if task_.match(repo) is False:
                log.debug(
                    "Repository does not match", repository=str(repo), task=task_.name
                )
                continue

            log.info("Matched repository", repository=str(repo), task=task_.name)
            result: RunResult = runner.execute(task_, repo)
            if result != RunResult.NO_CHANGES:
                changes_total += 1

            if task_.change_limit is not None and changes_total >= task_.change_limit:
                log.info(
                    "Limit of changes reached",
                    limit=task_.change_limit,
                    task=task_.name,
                )
                return success

        except Exception:
            log.exception("Task failed", repository=str(repo), task=task_.name)
            success = False

    return success


def options_from_config(path: str) -> Options:
    cfg = config.read_config_from_file(path)
    return config_to_options(cfg)


def config_to_options(cfg: config.Config) -> Options:
    opts = Options(cfg)

    opts.encoding_registry = encoding.Registry()
    opts.encoding_registry.register(
        encoding.Json(cfg.json_.indent), cfg.json_.extensions
    )
    opts.encoding_registry.register(encoding.Toml(), cfg.toml.extensions)
    opts.encoding_registry.register(
        encoding.Yaml(cfg.yaml.explicit_start), cfg.yaml.extensions
    )

    if cfg.github.access_token != "":
        source_github = source.Github(cfg.github.access_token, cfg.github.base_url)
        opts.sources["github"] = source_github

    if cfg.gitlab.private_token != "":
        source_gitlab = source.Gitlab(cfg.gitlab.url, cfg.gitlab.private_token)
        opts.sources["gitlab"] = source_gitlab

    return opts


def create_template_mapping(repo: source.Repository) -> dict[str, str]:
    return {
        "repo_name": repo.name,
        "repo_project": repo.project,
        "repo_source": repo.source,
    }
