from rcmt import Run
from rcmt.matcher import RepoName

with Run(name="python-defaults") as run:
    run.add_matcher(RepoName("github.com/MyOrg/.+"))
    run.add_package("flake8")
