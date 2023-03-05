from rcmt import Task
from rcmt.matcher import RepoName

with Task(name="templating-example") as task:
    task.add_matcher(RepoName(search="github.com/MyOrg/.+"))

    task.add_package("flake8")
