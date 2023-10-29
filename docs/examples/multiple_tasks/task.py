"""
This Task file contains two Tasks. Each Task will be executed
independent of the other and create its own pull request(s).

This is great for sharing functionality between Tasks or group
related Tasks together in one file.
"""
from rcmt import Task, context, register_task
from rcmt.action import own
from rcmt.filter import repo_name


class FirstTask(Task):
    def filter(self, ctx: context.Context) -> bool:
        return repo_name(ctx=ctx, search="github.com/MyOrg/.+")

    def apply(self, ctx: context.Context) -> None:
        own(ctx=ctx, content="Example One", target="example-one.txt")


class SecondTask(Task):
    def filter(self, ctx: context.Context) -> bool:
        return repo_name(ctx=ctx, search="github.com/MyOrg/.+")

    def apply(self, ctx: context.Context) -> None:
        own(ctx=ctx, content="Example Two", target="example-two.txt")


# Register both tasks. Can be done in one fucntion call.
register_task(FirstTask(), SecondTask())
