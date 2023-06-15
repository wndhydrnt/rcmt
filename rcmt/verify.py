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
        result: bool = True
        t = task.read(task_path)
        for m in t.matchers:
            if m.match(repository) is True:
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
        gitc = rcmt.git.Git(
            t.branch(opts.config.git.branch_prefix),
            opts.config.git.clone_options,
            directory,
            opts.config.git.user_name,
            opts.config.git.user_email,
        )

        print("🏗️  Preparing git clone", file=out)
        checkout_dir = gitc.prepare(repository)
        tpl_mapping: dict[str, str] = create_template_mapping(repository)
        print("🚜 Applying actions", file=out)
        apply_actions(
            repo=repository, task_=t, tpl_mapping=tpl_mapping, work_dir=checkout_dir
        )
        if gitc.has_changes(repo_dir=checkout_dir):
            print(
                f"😍 Actions modified files - view changes in {checkout_dir}", file=out
            )
        else:
            print("🤔 No changes after applying Actions", file=out)
