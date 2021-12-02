from rcmt import Run
from rcmt.matcher import RepoName

with Run(name="templating-example") as run:
    run.add_matcher(RepoName(search="github.com/MyOrg/.+"))

    run.add_package("flake8")
