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
