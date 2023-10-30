from rcmt import Task, context, register_task
from rcmt.action import own
from rcmt.filter import repo_name


class PythonDefaults(Task):
    def filter(self, ctx: context.Context) -> bool:
        return repo_name(ctx=ctx, search="github.com/MyOrg/.+")

    def apply(self, ctx: context.Context) -> None:
        own(
            ctx=ctx,
            # Load the content to write from a file.
            # The path to the file is relative to task.py.
            content=self.load_file(".flake8"),
            # Path to the target where rcmt writes the content of source.
            # This is relative to the root path of a repository.
            target=".flake8",
        )


register_task(PythonDefaults())
