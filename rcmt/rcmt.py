import datetime
import logging
import sys
from typing import Optional

import structlog

from . import config, encoding, git, run, source
from .log import SECRET_MASKER
from .source.local import Local

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        SECRET_MASKER.process_event,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
        structlog.dev.ConsoleRenderer(
            colors=sys.stdout is not None and sys.stdout.isatty()
        ),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

log: structlog.stdlib.BoundLogger = structlog.get_logger()


class Options:
    def __init__(self, cfg: config.Config):
        self.config = cfg
        self.encoding_registry: encoding.Registry = encoding.Registry()
        self.run_paths: list[str] = []
        self.sources: dict[str, source.Base] = {}


def can_merge_after(
    created_at: datetime.datetime, delay: Optional[datetime.timedelta]
) -> bool:
    if delay is None:
        return True

    passed = datetime.datetime.now() - created_at
    return passed >= delay


class RepoRun:
    def __init__(self, g: git.Git, opts: Options):
        self.git = g
        self.opts = opts

    def execute(self, matcher: run.Run, repo: source.Repository):
        pr_identifier = repo.find_pull_request(self.git.branch_name)
        if pr_identifier is not None and repo.is_pr_closed(pr_identifier) is True:
            log.info(
                "Existing PR has been closed",
                branch=self.git.branch_name,
                repo=str(repo),
            )
            return

        if (
            pr_identifier is not None
            and repo.is_pr_merged(pr_identifier) is True
            and matcher.merge_once
        ):
            log.info(
                "Existing PR has been merged",
                branch=self.git.branch_name,
                repo=str(repo),
            )
            return

        work_dir = self.git.prepare(repo)
        tpl_mapping = create_template_mapping(repo)
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
        apply_actions(repo, matcher, tpl_mapping, work_dir)
        has_changes = False
        if self.git.has_changes(work_dir) is True:
            log.debug("Committing changes", repo=str(repo))
            self.git.commit_changes(work_dir, matcher.commit_msg)
            has_changes = True
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

            return

        # Combining self.git.needs_push and has_changes avoids an unnecessary push of the
        # branch if the remote branch does not exist.
        needs_push = self.git.needs_push(work_dir) and has_changes
        if needs_push:
            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not pushing changes")
            else:
                log.debug("Pushing changes", repo=str(repo))
                self.git.push(work_dir)

        if needs_push is True and (
            pr_identifier is None or repo.is_pr_merged(pr_identifier) is True
        ):
            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not creating pull request")
            else:
                log.info("Create pull request", repo=str(repo))
                repo.create_pull_request(self.git.branch_name, pr)

            return

        if (
            matcher.auto_merge is True
            and needs_push is False
            and pr_identifier is not None
            and repo.is_pr_open(pr_identifier) is True
        ):
            if not repo.has_successful_pr_build(pr_identifier):
                log.warn(
                    "Cannot merge because build of pull request failed", repo=str(repo)
                )
                return

            if not can_merge_after(
                repo.pr_created_at(pr_identifier), matcher.auto_merge_after
            ):
                log.info("Too early to merge pull request", repo=str(repo))
                return

            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not merging pull request", repo=str(repo))
            else:
                log.info("Merge pull request", repo=str(repo))
                repo.merge_pull_request(pr_identifier)

            return

        if pr_identifier is not None and repo.is_pr_open(pr_identifier) is True:
            repo.update_pull_request(pr_identifier, pr)


def apply_actions(
    repo: source.Repository,
    rrun: run.Run,
    tpl_mapping: dict,
    work_dir: str,
) -> None:
    for a in rrun.actions:
        log.debug(
            "Applying action from run",
            action=a.__class__.__name__,
            run=rrun.name,
            repo=str(repo),
        )
        a.apply(work_dir, tpl_mapping)


def execute(opts: Options) -> bool:
    log_level = logging.getLevelName(opts.config.log_level.upper())
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )
    repositories: list[source.Repository] = []
    for s in opts.sources.values():
        repositories += s.list_repositories()

    log.info("Repositories returned by sources", count=len(repositories))
    success = True
    for run_path in opts.run_paths:
        run_ = run.read(run_path)
        run_success = execute_run(run_, repositories, opts)
        if run_success is False:
            success = False

    if success is False:
        log.error("Errors during execution - check previous log messages")

    return success


def execute_local(
    directory: str, repo_source: str, repo_project: str, repo_name: str, opts: Options
) -> None:
    log_level = logging.getLevelName(opts.config.log_level.upper())
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )
    if len(opts.run_paths) == 0:
        log.warning("No path to a run file supplied")
        return
    matcher = run.read(opts.run_paths[0])
    repo = Local(repo_source, repo_project, repo_name)
    tpl_mapping: dict[str, str] = create_template_mapping(repo)
    apply_actions(repo, matcher, tpl_mapping, directory)


def execute_run(
    run_: run.Run,
    repos: list[source.Repository],
    opts: Options,
) -> bool:
    gitc = git.Git(
        run_.branch(opts.config.git.branch_prefix),
        opts.config.git.clone_options,
        opts.config.git.data_dir,
        opts.config.git.user_name,
        opts.config.git.user_email,
    )
    runner = RepoRun(gitc, opts)
    success = True
    for repo in repos:
        try:
            if run_.match(repo) is False:
                log.debug(
                    "Repository does not match", repository=str(repo), run=run_.name
                )
                continue

            log.info("Matched repository", repository=str(repo), run=run_.name)
            runner.execute(run_, repo)
        except Exception:
            log.exception("Run failed", repository=str(repo), run=run_.name)
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
