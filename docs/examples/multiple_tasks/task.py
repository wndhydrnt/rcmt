"""
This Task file contains two Tasks. Each Task will be executed independent of the other
and create its own pull request.

This is great for sharing functionality between Tasks or group related Tasks together in
one file.
"""
from rcmt import Task
from rcmt.action import Own
from rcmt.matcher import RepoName

with Task("First Task") as task:
    # Match all repositories of MyOrg.
    task.add_matcher(RepoName("github.com/MyOrg/.+"))

    # Create the file example-one.txt with content "Example One".
    task.add_action(Own(content="Example One", target="example-one.txt"))

with Task("Second Task") as task:
    # Match all repositories of MyOrg.
    task.add_matcher(RepoName("github.com/MyOrg/.+"))

    # Create the file example-two.txt with content "Example Two".
    task.add_action(Own(content="Example Two", target="example-two.txt"))
