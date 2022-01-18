import os.path

from rcmt.package import Manifest
from rcmt.package.action import Action


class HelloWorld(Action):
    """
    HelloWorld action creates the file "hello-world.txt" in the root of a repository.
    It writes "Hello World" to it.
    """

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        file = os.path.join(repo_path, "hello-world.txt")
        with open(file, "w+") as f:
            f.write("Hello World")
            f.write("\n")


with Manifest(name="custom-action") as manifest:
    manifest.add_action(HelloWorld())
