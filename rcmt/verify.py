import os.path
from typing import Optional, TextIO

import structlog

import rcmt.git
from rcmt import task
from rcmt.rcmt import Options, apply_actions, create_template_mapping
from rcmt.source import Repository

log: structlog.stdlib.BoundLogger = structlog.get_logger()


def execute(directory: str, opts: Options, out: TextIO, repo_name: str) -> None:
    repository: Optional[Repository] = None
    for source_name, source in opts.sources.items():
        repository = source.create_from_name(repo_name)
        if repository is not None:
            break

        log.debug("Source did not return a repository", source=source_name)

    if repository is None:
        log.error(f"No Source found for repository {repo_name}")
        return

    for task_path in opts.task_paths:
        task.read(task_path)

    for t in task.registry.tasks:
        result: bool = True
        for m in t.matchers:
            if m(repository) is True:
                print(f"✅ Matcher {str(m)} matches", file=out)
            else:
                result = False
                print(f"❌ Matcher {str(m)} does not match", file=out)

        if result is False:
            print(
                f"❌ - at least one Matcher did not match repository {repo_name}",
                file=out,
            )
            return

        print("---")
        checkout_dir = os.path.join(
            directory,
            repository.source,
            repository.project,
            repository.name,
        )
        gitc = rcmt.git.Git(
            base_branch=repository.base_branch,
            checkout_dir=checkout_dir,
            clone_opts=opts.config.git.clone_options,
            repository_name=str(repository),
            user_email=opts.config.git.user_email,
            user_name=opts.config.git.user_name,
        )

        print("🏗️  Preparing git clone", file=out)
        gitc.initialize(clone_url=repository.clone_url)
        gitc.prepare_branch(branch_name=t.branch(opts.config.git.branch_prefix))
        tpl_mapping: dict[str, str] = create_template_mapping(repository)
        print("🚜 Applying actions", file=out)
        apply_actions(
            repo=repository, task_=t, tpl_mapping=tpl_mapping, work_dir=checkout_dir
        )
        if gitc.has_changes_local():
            print(
                f"😍 Actions modified files - view changes in {checkout_dir}", file=out
            )
        else:
            print("🤔 No changes after applying Actions", file=out)
