from rcmt import Context, Task
from rcmt.action import Seed
from rcmt.filter import RepoName

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


with Task("custom-templating", pr_body=pr_body, pr_title=pr_title) as task:
    task.add_filter(RepoName(f"^{REPOSITORY}$"))
    task.add_filter(set_custom_template_var)

    task.add_action(Seed(content="Custom Templating", target="templating.txt"))
