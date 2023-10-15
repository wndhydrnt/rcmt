# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
