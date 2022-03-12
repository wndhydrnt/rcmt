from ..fs import FileProxy
from .action import Action


class Manifest:
    """
    The Manifest describes the :doc:`Actions <action>` that rcmt applies to each
    repository. Every Package contains at least a Manifest file. The name of the
    Manifest file is ``manifest.py``.

    :param name: Name of the Manifest.

    **Example**

    Take a look at the `simple example <https://github.com/wndhydrnt/rcmt/tree/main/docs/examples/simple>`_
    on GitHub.
    """

    def __init__(self, name: str):
        self.name = name

        self.actions: list[Action] = []
        self.file_proxies: list[FileProxy] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_action(self, action: Action) -> None:
        """
        Adds an Action. rcmt applies Actions in the order in which they are added to the
        Manifest.

        :param action: The Action to add.
        """
        self.actions.append(action)

    def load_file(self, path: str) -> FileProxy:
        fp = FileProxy(path)
        self.file_proxies.append(fp)
        return fp

    def set_path(self, path):
        for fp in self.file_proxies:
            fp.set_path(path)
