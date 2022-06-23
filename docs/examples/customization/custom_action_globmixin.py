from rcmt.action import Action, GlobMixin
from rcmt.package import Manifest


class HelloWorld(GlobMixin, Action):
    """
    HelloWorld action appends the string "Hello World" to the end of each file that
    matches the glob selector.
    """

    def process_file(self, path: str, tpl_data: dict):
        with open(path, "a") as f:
            f.write("Hello World")


with Manifest(name="custom-action") as manifest:
    # This selector matches all files with the extension "txt" in the root of a repository.
    manifest.add_action(HelloWorld(selector="*.txt"))
