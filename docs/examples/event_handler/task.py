from rcmt import Context, Task
from rcmt.action import Seed
from rcmt.filter import RepoName

# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt"


def handle_pr_created(ctx: Context) -> None:
    print("Pull request created")


with Task("event-handler") as task:
    task.add_filter(RepoName(f"^{REPOSITORY}$"))

    task.add_action(Seed(content="Hello World", target="hello.txt"))

    task.on_pr_created(handle_pr_created)
