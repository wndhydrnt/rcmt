"""
This file demonstrates the various ways to create an Action.
An Action is a function that brings one or more files into a desired state.
The function receives the path to the clone of a repository as well as data
it can use for templating.
All Actions in this file do the same thing:
Create the file "hello.txt" in the root of the repository.
"""
import os.path

from rcmt import Task
from rcmt.action import Action, Own


class ActionAsClass(Action):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        path = os.path.abspath(os.path.join(repo_path, self.file_name))
        with open(path, "w") as f:
            f.write("Hello rcmt")


class ActionAsCallableClass:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def __call__(self, repo_path: str, tpl_data: dict) -> None:
        path = os.path.abspath(os.path.join(repo_path, self.file_name))
        with open(path, "w") as f:
            f.write("Hello rcmt")


def action_as_function(repo_path: str, tpl_data: dict) -> None:
    path = os.path.abspath(os.path.join(repo_path, "hello.txt"))
    with open(path, "w") as f:
        f.write("Hello rcmt")


with Task(name="action-example") as task:
    task.add_action(Own(content="Hello rcmt", target="hello.txt"))
    task.add_action(ActionAsClass(file_name="hello.txt"))
    task.add_action(ActionAsCallableClass(file_name="hello.txt"))
    task.add_action(action_as_function)
