from typing import Optional

import structlog

from rcmt import task
from rcmt.rcmt import Options
from rcmt.source import Repository

log: structlog.stdlib.BoundLogger = structlog.get_logger()


def matchers(opts: Options, repo_name: str) -> None:
    repository: Optional[Repository] = None
    for source in opts.sources.values():
        repository = source.create_from_name(repo_name)
        if repository is not None:
            break

    if repository is None:
        log.error("No Source found for name", name=repo_name)
        return

    for task_path in opts.task_paths:
        result: bool = True
        t = task.read(task_path)
        for m in t.matchers:
            if m.match(repository) is True:
                print(f"✅ Matcher {str(m)} matches")
            else:
                result = False
                print(f"❌ Matcher {str(m)} does not match")

        print("---")
        if result is True:
            print("Result: ✅")
        else:
            print(
                f"Result: ❌ - at least one Matcher did not match repository {repo_name}"
            )
