import datetime
import logging
import re
from typing import Optional

import structlog
import yaml

from rcmt import action, config, encoding, git, package, source

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

log = structlog.get_logger()


class Options:
    def __init__(self, cfg: config.Config):
        self.config = cfg
        self.action_registry: action.Registry = action.Registry()
        self.encoding_registry: encoding.Registry = encoding.Registry()
        self.matcher_path: str = ""
        self.packages_paths: list[str] = []
        self.sources: list[source.SourceLister] = []


def can_merge_after(
    created_at: datetime.datetime, delay: Optional[datetime.timedelta]
) -> bool:
    if delay is None:
        return True

    passed = datetime.datetime.now() - created_at
    return passed >= delay


class Run:
    def __init__(self, g: git.Git, opts: Options):
        self.git = g
        self.opts = opts

    def execute(
        self,
        matcher: config.Matcher,
        pkgs: list[package.Package],
        repo: source.Repository,
    ):
        work_dir = self.git.prepare(repo)
        tpl_mapping = {"repo_name": repo.name, "repo_project": repo.project}
        pr = source.PullRequest(
            self.opts.config.pr_title_prefix,
            self.opts.config.pr_title_body.format(matcher_name=matcher.name),
            self.opts.config.pr_title_suffix,
            matcher.pr_body,
            matcher.pr_title,
        )
        has_changes = False
        for pkg in pkgs:
            for a in pkg.actions:
                log.debug(
                    "Applying action",
                    action=a.__class__.__name__,
                    pkg=pkg.name,
                    repo=str(repo),
                )
                a.apply(work_dir, tpl_mapping)

            if self.git.has_changes(work_dir) is True:
                log.debug("Committing changes", pkg=pkg.name, repo=str(repo))
                self.git.commit_changes(work_dir, f"rcmt: Applied package {pkg.name}")
                pr.add_package(pkg.name)
                has_changes = True

            else:
                log.info(
                    "No changes after applying package", pkg=pkg.name, repo=str(repo)
                )

        # Combining self.git.needs_push and has_changes avoids an unnecessary push of the
        # branch if the remote branch does not exist.
        needs_push = self.git.needs_push(work_dir) and has_changes
        if needs_push:
            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not pushing changes")
            else:
                log.debug("Pushing changes", repo=str(repo))
                self.git.push(work_dir)

        open_pr_identifier = repo.find_open_pull_request(self.git.branch_name)
        if needs_push is True and open_pr_identifier is None:
            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not creating pull request")
            else:
                log.info("Create pull request", repo=str(repo))
                repo.create_pull_request(self.git.branch_name, pr)

        if (
            self.opts.config.auto_merge is True
            and needs_push is False
            and open_pr_identifier is not None
        ):
            if not repo.has_successful_pr_build(open_pr_identifier):
                log.warn(
                    "Cannot merge because build of pull request failed", repo=str(repo)
                )
                return

            if not can_merge_after(
                repo.pr_created_at(open_pr_identifier), matcher.auto_merge_after
            ):
                log.info("Too early to merge pull request", repo=str(repo))
                return

            if self.opts.config.dry_run:
                log.warn("DRY RUN: Not merging pull request", repo=str(repo))
            else:
                log.info("Merge pull request", repo=str(repo))
                repo.merge_pull_request(open_pr_identifier)


def run(opts: Options):
    log_level = logging.getLevelName(opts.config.log_level.upper())
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )

    pkg_reader = package.PackageReader(opts.action_registry, opts.encoding_registry)
    pkgs = pkg_reader.read_packages(opts.packages_paths)
    matcher = parse_matcher(opts.matcher_path)
    pkgs_to_apply = find_packages(matcher.packages, pkgs)
    repositories = []
    for s in opts.sources:
        repositories += s.list_repositories()

    log.info("Repositories returned by sources", count=len(repositories))
    matched_repos = match_repositories(repositories, matcher.match)
    gitc = git.Git(
        opts.config.git.branch_name,
        opts.config.git.data_dir,
        opts.config.git.user_name,
        opts.config.git.user_email,
    )
    runner = Run(gitc, opts)
    for repo in matched_repos:
        log.info("Matched repository", repository=str(repo))
        runner.execute(matcher, pkgs_to_apply, repo)


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

    opts.action_registry.add("delete_key", action.DeleteKey.factory)
    opts.action_registry.add("exec", action.exec_factory)
    opts.action_registry.add("merge", action.Merge.factory)
    opts.action_registry.add("line_in_file", action.line_in_file_factory)
    opts.action_registry.add("own", action.own_factory)
    opts.action_registry.add("seed", action.seed_factory)

    if cfg.github.access_token != "":
        source_github = source.Github(cfg.github.access_token)
        opts.sources.append(source_github)

    if cfg.gitlab.private_token != "":
        source_gitlab = source.Gitlab(cfg.gitlab.url, cfg.gitlab.private_token)
        opts.sources.append(source_gitlab)

    return opts


def match_repositories(
    repositories: list[source.Repository], match: config.Match
) -> list[source.Repository]:
    pattern = match.repository_regex
    matched_repositories = []
    for repo in repositories:
        match_str = str(repo)
        result = pattern.match(match_str)
        if result is not None:
            matched_repositories.append(repo)

    return matched_repositories


def parse_matcher(path: str) -> config.Matcher:
    with open(path, "r") as f:
        raw = yaml.load(f, Loader=yaml.FullLoader)

    return config.Matcher(**raw)


def find_packages(
    pkg_names: list[str], pkgs: list[package.Package]
) -> list[package.Package]:
    pkgs_found = []
    pkg_names_found = []
    for pkg in pkgs:
        if pkg.name in pkg_names:
            pkg_names_found.append(pkg.name)
            pkgs_found.append(pkg)

    unknown_pkg_names = list(set(pkg_names).difference(pkg_names_found))
    if len(unknown_pkg_names) > 0:
        raise RuntimeError(f"unknown packages {unknown_pkg_names}")

    return pkgs_found
