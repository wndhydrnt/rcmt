from rcmt import Context, Task, register_task
from rcmt.action import seed
from rcmt.filter import repo_name

# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt"


class EventHandlerExample(Task):
    def filter(self, ctx: Context) -> bool:
        return repo_name(ctx=ctx, search=f"^{REPOSITORY}$")

    def apply(self, ctx: Context) -> None:
        seed(ctx=ctx, content="Hello World", target="hello.txt")

    def on_pr_closed(self, ctx: Context) -> None:
        print("pull request closed")

    def on_pr_created(self, ctx: Context) -> None:
        print("pull request created")

    def on_pr_merged(self, ctx: Context) -> None:
        print("pull request merged")


register_task(EventHandlerExample())
