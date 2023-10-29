from rcmt import Task, context, register_task
from rcmt.action import line_in_file
from rcmt.filter import repo_name


class GitIgnoreVSCodeDir(Task):
    def filter(self, ctx: context.Context) -> bool:
        # Match all repositories in MyOrg on GitHub
        return repo_name(ctx=ctx, search="github.com/MyOrg/.*")

    def apply(self, ctx: context.Context) -> None:
        # Add the Action LineInFile to the Task.
        # LineInFile ensures that the given `line` exists in the file.
        line_in_file(line=".vscode/", target=".gitignore")


register_task(GitIgnoreVSCodeDir())
