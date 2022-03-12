import os.path
from typing import Union


class FileProxy:
    def __init__(self, file_path: str):
        self.file_path = file_path

        self.path = ""

    def set_path(self, path: str):
        self.path = path

    def read(self) -> str:
        with open(os.path.join(self.path, self.file_path), "r") as f:
            return f.read()


def read_file_or_str(content: Union[str, FileProxy]) -> str:
    if isinstance(content, FileProxy):
        return content.read()

    return content
