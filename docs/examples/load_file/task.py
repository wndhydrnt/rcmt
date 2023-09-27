from rcmt import Task
from rcmt.action import Own
from rcmt.matcher import RepoName

# rcmt uses the name when committing changes.
with Task(name="python-defaults") as task:
    # Match all repositories of MyOrg.
    task.add_matcher(RepoName("github.com/MyOrg/.+"))
    # Add an action to the task. The action tells rcmt what to do.
    # The Own action creates a file and ensures that its content stays the same.
    task.add_action(
        Own(
            # Load the content to write from a file.
            # The path to the file is relative to task.py.
            content=task.load_file(".flake8"),
            # Path to the target where rcmt writes the content of source.
            # This is relative to the root path of a repository.
            target=".flake8",
        )
    )
