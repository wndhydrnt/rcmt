from rcmt import Context, Task
from rcmt.action import seed
from rcmt.filter import repo_name

# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt"


pr_title = "Demonstrate templating in {{repo_name}}"
pr_body = """Host: {{repo_host}}

Owner: {{repo_owner}}

Name: {{repo_name}}"""


class TemplatingWithDefaultVars(Task):
    pr_title = pr_title
    pr_body = pr_body

    def filter(self, ctx: Context) -> bool:
        return repo_name(ctx=ctx, search=f"^{REPOSITORY}$")

    def apply(self, ctx: Context) -> None:
        seed(ctx=ctx, content="Default Templating", target="templating.txt")
