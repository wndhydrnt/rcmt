import logging
import re

import structlog
import yaml

from rcmt import action, config, encoding, git, package, source

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)

log = structlog.get_logger()


class Options:
    def __init__(self, cfg: config.Config):
        self.config = cfg
        self.action_registry: action.Registry = action.Registry()
        self.encoding_registry: encoding.Registry = encoding.Registry()
        self.sources: list[source.SourceLister] = []


def run(opts: Options):
    pkg_reader = package.PackageReader(opts.action_registry, opts.encoding_registry)
    pkgs = pkg_reader.read_packages(opts.config.packages_path)
    match_cfg = parse_match_config(opts.config.run_path)
    pkgs_to_apply = find_packages(match_cfg.packages, pkgs)
    repositories = []
    for s in opts.sources:
        repositories += s.list_repositories()

    matched_repos = match_repositories(repositories, match_cfg.match)
    gitc = git.Git(opts.config.git.branch_name, opts.config.git.data_dir)
    for repo in matched_repos:
        log.info("Matched repository", repository=str(repo))
        work_dir = gitc.prepare(repo)
        tpl_mapping = {"repo_name": repo.name, "repo_project": repo.project}
        for pkg in pkgs_to_apply:
            for a in pkg.actions:
                log.debug(
                    "Applying action",
                    action=a.action.__class__.__name__,
                    name=a.name,
                    pkg=pkg.name,
                    repo=str(repo),
                )
                a.apply(work_dir, tpl_mapping)

            if gitc.has_changes(work_dir) is True:
                log.debug("Committing changes", pkg=pkg.name, repo=str(repo))
                gitc.commit_changes(
                    work_dir, f"rcmt: Applied {match_cfg.name} package {pkg.name}"
                )
            else:
                log.debug(
                    "No changes after applying package", pkg=pkg.name, repo=str(repo)
                )

        needs_push = gitc.needs_push(work_dir)
        if needs_push:
            if opts.config.dry_run:
                log.info("DRY RUN: Not pushing changes")
            else:
                log.debug("Pushing changes", repo=str(repo))
                gitc.push(work_dir)

        open_pr_identifier = repo.find_open_pull_request(gitc.branch_name)
        if needs_push is True and open_pr_identifier is None:
            if opts.config.dry_run:
                log.info("DRY RUN: Not creating pull request")
            else:
                log.info("Create pull request", repo=str(repo))
                repo.create_pull_request(
                    gitc.branch_name, create_pr_title(opts.config), ""
                )

        if (
            opts.config.auto_merge is True
            and needs_push is False
            and open_pr_identifier is not None
        ):
            if repo.has_successful_pr_build(open_pr_identifier):
                if opts.config.dry_run:
                    log.info("DRY RUN: Not merging pull request", repo=str(repo))
                else:
                    log.info("Merge pull request", repo=str(repo))
                    repo.merge_pull_request(open_pr_identifier)
            else:
                log.warn(
                    "Cannot merge because build of pull request failed", repo=str(repo)
                )


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

    opts.action_registry.add("delete_keys", action.DeleteKeys.factory)
    opts.action_registry.add("exec", action.exec_factory)
    opts.action_registry.add("merge", action.Merge.factory)
    opts.action_registry.add("own", action.own_factory)
    opts.action_registry.add("seed", action.seed_factory)

    if cfg.github.access_token != "":
        source_github = source.Github(cfg.github.access_token)
        opts.sources.append(source_github)

    return opts


def match_repositories(
    repositories: list[source.Repository], match: str
) -> list[source.Repository]:
    pattern = re.compile(match)
    matched_repositories = []
    for repo in repositories:
        match_str = str(repo)
        result = pattern.match(match_str)
        if result is not None:
            matched_repositories.append(repo)

    return matched_repositories


def parse_match_config(path: str) -> config.Run:
    with open(path, "r") as f:
        raw = yaml.load(f, Loader=yaml.FullLoader)

    return config.Run(**raw)


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


def create_pr_title(cfg: config.Config) -> str:
    return f"{cfg.pr_title_prefix} {cfg.pr_title_body} {cfg.pr_title_suffix}"
