from rcmt import Task
from rcmt.action import Seed
from rcmt.matcher import RepoName

# Replace with your repository.
REPOSITORY = "github.com/wndhydrnt/rcmt"


pr_title = "Demonstrate templating in {{repo_name}}"
pr_body = """Host: {{repo_host}}

Owner: {{repo_owner}}

Name: {{repo_name}}"""


with Task("default-templating") as task:
    task.add_matcher(RepoName(f"^{REPOSITORY}$"))

    task.add_action(Seed(content="Default Templating", target="templating.txt"))
