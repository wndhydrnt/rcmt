from rcmt import Context, Task, context, register_task
from rcmt.action import seed
from rcmt.filter import repo_name

# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt"


def set_custom_template_var(ctx: Context) -> bool:
    ctx.set_template_key("greet", "Hello World")
    return True


pr_title = "Demonstrate custom templating"
pr_body = """Custom filter says:
{% if greet %}
{{ greet }}
{% else %}
Nothing to say.
{% endif %}
"""


class TemplatingWithCustomVars(Task):
    pr_title = pr_title
    pr_body = pr_body

    def filter(self, ctx: context.Context) -> bool:
        ctx.set_template_key("greet", "Hello World")
        return repo_name(ctx=ctx, search=f"^{REPOSITORY}$")

    def apply(self, ctx: context.Context) -> None:
        seed(ctx=ctx, content="Custom Templating", target="templating.txt")


register_task(TemplatingWithCustomVars())
