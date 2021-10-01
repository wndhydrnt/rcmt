import os


class FileLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self, pkg_path: str) -> str:
        p = os.path.join(pkg_path, self.path)
        with open(p, "r") as f:
            return f.read()
