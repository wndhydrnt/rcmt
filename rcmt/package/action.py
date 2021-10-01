import io
import os
import pathlib
import string
import subprocess
from typing import Union

import mergedeep

from rcmt import encoding, util

from .loader import FileLoader


def load_file_or_str(input: Union[str, FileLoader], pkg_path: str) -> str:
    if isinstance(input, str):
        return input

    if isinstance(input, FileLoader):
        return input.load(pkg_path)


class Action:
    """
    Action is the abstract class that defines the interface each action implements.
    """

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        """
        apply modifies a file in a repository.

        :param repo_path: The absolute path to the file in a repository to modify.
        :param tpl_data: The content of the file from a package, already populated with
                         template data.
        :return: None
        """
        raise NotImplementedError("class does not implement Action.apply()")


class Absent(Action):
    def __init__(self, target):
        self.target = target

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.exists(repo_file_path):
            os.remove(repo_file_path)


class Own(Action):
    def __init__(self, target: str, source: Union[str, FileLoader]):
        self.source = source
        self.target = target

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        data = load_file_or_str(self.source, pkg_path)
        file_path = os.path.join(repo_path, self.target)
        with open(file_path, "w+") as f:
            f.write(string.Template(data).substitute(tpl_data))


class Seed(Own):
    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.isfile(repo_file_path):
            return

        super().apply(pkg_path, repo_path, tpl_data)


class EncodingAware:
    def __init__(self):
        self._encodings: encoding.Registry

    @property
    def encodings(self) -> encoding.Registry:
        return self._encodings

    @encodings.setter
    def encodings(self, er: encoding.Registry):
        self._encodings = er


class Merge(Action, EncodingAware):
    def __init__(
        self,
        selector: str,
        source: Union[str, FileLoader],
        merge_strategy="replace",
    ):
        super().__init__()
        self.selector = selector
        self.source_data = source
        self.strategy = mergedeep.Strategy.REPLACE
        if merge_strategy == "additive":
            self.strategy = mergedeep.Strategy.ADDITIVE

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        data = string.Template(load_file_or_str(self.source_data, pkg_path)).substitute(
            tpl_data
        )
        paths = util.iglob(repo_path, self.selector)
        for p in paths:
            ext = pathlib.Path(p).suffix
            enc = self.encodings.get_for_extension(ext)
            with open(p, "r") as f:
                orig_data = enc.decode(f)

            tpl = enc.decode(io.StringIO(data))
            merged_data = enc.merge(orig_data, tpl, self.strategy)
            with open(p, "w") as f:
                enc.encode(f, merged_data)


class DeleteKey(Action, EncodingAware):
    def __init__(self, key: str, target: str):
        super().__init__()
        self.key_path = key.split(".")
        self.target = target

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        ext = pathlib.Path(repo_file_path).suffix
        enc = self.encodings.get_for_extension(ext)
        with open(repo_file_path, "r") as f:
            orig_data: dict = enc.decode(f)

        new_data = self.process_recursive(self.key_path, orig_data)
        with open(repo_file_path, "w") as f:
            enc.encode(f, new_data)

    @classmethod
    def process_recursive(cls, query: list[str], data: dict) -> dict:
        if len(query) == 0:
            return data

        qk = query[0]
        if qk not in data:
            return data

        if isinstance(data[qk], dict):
            data[qk] = cls.process_recursive(query[1:], data[qk])
        else:
            del data[qk]

        return data


class Exec(Action):
    def __init__(self, exec_path: str, selector: str, timeout: int):
        self.exec_path = exec_path
        self.selector = selector
        self.timeout = timeout

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        repo_file_paths = util.iglob(repo_path, self.selector)
        for repo_file_path in repo_file_paths:
            result = subprocess.run(
                args=[self.exec_path, repo_file_path],
                capture_output=True,
                shell=True,
                timeout=self.timeout,
            )
            if result.returncode > 0:
                raise RuntimeError(
                    f"""Exec action call to {self.exec_path} failed.
    stdout: {result.stdout.decode('utf-8')}
    stderr: {result.stderr.decode('utf-8')}"""
                )


class LineInFile(Action):
    def __init__(self, line: str, selector: str):
        self.line = line.strip()
        self.selector = selector

    def apply(self, pkg_path: str, repo_path: str, tpl_data: dict) -> None:
        repo_file_paths = util.iglob(repo_path, self.selector)
        for repo_file_path in repo_file_paths:
            with open(repo_file_path, "r") as f:
                for line in f:
                    if line.strip() == self.line:
                        return None

            with open(repo_file_path, "a") as f:
                f.write(self.line)
                f.write("\n")
