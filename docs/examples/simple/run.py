from rcmt import Run
from rcmt.matcher import RepoName
from rcmt.package.action import Own

# rcmt uses the name when committing changes.
with Run(name="python-defaults") as run:
    content = """[flake8]
max-line-length = 88
extend-ignore = E203
"""

    # Match all repositories of MyOrg.
    run.add_matcher(RepoName("github.com/MyOrg/.+"))
    # Add an action to the run. The action tells rcmt what to do.
    # The Own action creates a file and ensures that its content stays the same.
    run.add_action(
        Own(
            # The content of the file to write.
            content=content,
            # Path to the target where rcmt writes the content of source.
            # This is relative to the root path of a repository.
            target=".flake8",
        )
    )
