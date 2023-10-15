from rcmt import Task
from rcmt.action import LineInFile
from rcmt.filter import RepoName

# rcmt uses the name to create the branch.
with Task("git-ignore-vscode-dir") as task:
    # Match all repositories in MyOrg on GitHub
    task.add_filter(RepoName("github.com/MyOrg/.*"))
    # Add the Action LineInFile to the Task.
    # LineInFile ensures that the given `line` exists in the file.
    task.add_action(LineInFile(line=".vscode/", selector=".gitignore"))
