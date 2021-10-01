from .action import Action
from .loader import FileLoader


class Manifest:
    def __init__(self, name: str):
        self.name = name

        self.actions: list[Action] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_action(self, action: Action):
        self.actions.append(action)

    def load_file(self, path: str) -> FileLoader:
        return FileLoader(path)
