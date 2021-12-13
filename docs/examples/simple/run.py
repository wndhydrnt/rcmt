from rcmt import Run
from rcmt.matcher import RepoName

# rcmt uses the name when committing changes.
with Run(name="python-defaults") as run:
    # Match all repositories of MyOrg.
    run.add_matcher(RepoName("github.com/MyOrg/.+"))
    # The name of a package to apply to all matching repositories.
    # "flake8" is the name set in the manifest.py file of the
    # flake8 package.
    run.add_package("flake8")
