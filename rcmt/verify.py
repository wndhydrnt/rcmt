# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Optional, TextIO

import structlog

import rcmt.git
from rcmt import fs, task
from rcmt.context import Context
from rcmt.rcmt import Options
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
        ctx = Context(repository)
        if t.filter(ctx=ctx) is True:
            print(f"✅ Filter of task {t.name} matches", file=out)
        else:
            print(
                f"❌ Filter of task {t.name} does not match repository {repo_name}",
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
        checkout_dir, has_conflict = gitc.prepare(force_rebase=False, repo=repository)
        print("🚜 Applying Task", file=out)
        with fs.in_checkout_dir(checkout_dir):
            t.apply(ctx=ctx)

        if gitc.has_changes_local(repo_dir=checkout_dir):
            print(
                f"😍 Actions modified files - view changes in {checkout_dir}", file=out
            )
        else:
            print("⚠️  No changes after applying Actions", file=out)
