"""
Actions encapsulate behavior of how to change a file.
"""

import io
import os
import pathlib
import subprocess
from typing import Callable

from rcmt import encoding


class Action:
    """
    Action is the abstract class that defines the interface each action implements.
    """

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        """
        apply modifies a file in a repository.

        :param repo_file_path: The absolute path to the file in a repository to modify.
        :param tpl_data: The content of the file from a package, already populated with
                         template data.
        :return: None
        """
        raise NotImplementedError("class does not implement Action.apply()")


class Own(Action):
    """
    Own ensures that a file in a repository stays the same.

    It always overwrites the data in the file with the data from a package.

    **Usage**

    .. code-block:: yaml

       name: own_example
       actions:
         - action: own
           file: config.yaml

    **Options**

    This action does not have any options.
    """

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        with open(repo_file_path, "w+") as f:
            f.write(tpl_data)


def own_factory(er: encoding.Registry, opts: dict) -> Own:
    return Own()


class Seed(Own):
    """
    Seed ensures that a file in a repository is present.

    It does not modify the file again if the file is present in a repository.

    **Usage**

    .. code-block:: yaml

       name: seed_example
       actions:
         - action: seed
           file: config.yaml

    **Options**

    This action does not have any options.
    """

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        if os.path.isfile(repo_file_path):
            return

        super().apply(repo_file_path, tpl_data)


def seed_factory(er: encoding.Registry, opts: dict) -> Seed:
    return Seed()


class Merge(Action):
    """
    Merge merges the content of a file in a repository with the content of a file from a
    package.

    It supports merging of various file formats through Encodings<<link>>.

    **Usage**

    .. code-block:: yaml

       # Declaration in Manifest of Package
       name: merge_example
       actions:
         - action: merge
           file: config.yaml

    .. code-block:: yaml

       # config.yaml in Package
       database:
         host: new.example.local
         username: abc
         ssl: true

    .. code-block:: yaml

       # config.yaml in a repository
       database:
         host: old.example.local
         username: abc

    .. code-block:: yaml

       # Result after merge
       database:
         host: new.example.local
         username: abc
         ssl: true

    **Options**

    This action does not have any options.
    """

    def __init__(self, encodings: encoding.Registry):
        self.encodings = encodings

    @staticmethod
    def factory(er: encoding.Registry, opts: dict):
        return Merge(er)

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        ext = pathlib.Path(repo_file_path).suffix
        enc = self.encodings.get_for_extension(ext)
        with open(repo_file_path, "r") as f:
            orig_data = enc.decode(f)

        tpl = enc.decode(io.StringIO(tpl_data))
        merged_data = enc.merge(orig_data, tpl)
        with open(repo_file_path, "w") as f:
            enc.encode(f, merged_data)


class DeleteKeys(Action):
    """
    DeleteKeys deletes a key from a dictionary.

    **Usage**

    .. code-block:: yaml

       name: delete_keys_example
       actions:
         - action: delete_keys
           file: config.yaml
           opts:
             keys:
               - "foo.bar.baz"

    Deletes the key `baz` and everything under it.

    Before:

    .. code-block:: yaml

       foo:
         bar:
           baz: to be deleted
        other: keep this

    After:

    .. code-block:: yaml

       foo:
         bar: {}
        other: keep this

    **Options**

    * `keys`: A list of strings where each entry is a path to the key to delete.
      (required)
    """

    def __init__(self, encodings: encoding.Registry):
        self.encodings = encodings

    @staticmethod
    def factory(er: encoding.Registry, opts: dict):
        return DeleteKeys(er)

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
        ext = pathlib.Path(repo_file_path).suffix
        enc = self.encodings.get_for_extension(ext)
        with open(repo_file_path, "r") as f:
            orig_data: dict = enc.decode(f)

        query: dict = enc.decode(io.StringIO(tpl_data))
        new_data = self.process_recursive(query, orig_data)
        with open(repo_file_path, "w") as f:
            enc.encode(f, new_data)

    @classmethod
    def process_recursive(cls, query: dict, data: dict) -> dict:
        for qk in query.keys():
            if qk not in data:
                continue

            if isinstance(query[qk], dict) and isinstance(data[qk], dict):
                data[qk] = cls.process_recursive(query[qk], data[qk])
            else:
                del data[qk]

        return data


class Exec(Action):
    """
    Exec calls an executable. This action allows modifications of files that cannot be
    modified in Python, e.g. source code of other programming languages.

    The executable needs to accept the path to a file in a repository as a parameter:

    .. code-block:: bash

       /my-program /tmp/rcmt/data/github/rcmt-test/file.py

    **Usage**

    .. code-block:: yaml

       name: exec_example
       actions:
         - action: exec
           file: config.yaml
           opts:
             exec_path: /home/me/my-program
             timeout: 30

    **Options**

    * `exec_path`: Path to the executable to call. (required)
    * `timeout`: Duration, in seconds, after which execution stops. Passes this option to subprocess.run(). (default: `120`)

    """

    def __init__(self, exec_path: str, timeout: int):
        self.exec_path = exec_path
        self.timeout = timeout

    def apply(self, repo_file_path: str, tpl_data: str) -> None:
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


def exec_factory(er: encoding.Registry, opts: dict) -> Exec:
    exec_path = opts.get("exec_path")
    if exec_path is None:
        raise RuntimeError("Exec Action: Required option exec_path not set")

    timeout = opts.get("timeout") or 120
    return Exec(exec_path, timeout)


class Registry:
    def __init__(self):
        self.factories: dict[str, Callable[[encoding.Registry, dict], Action]] = {}

    def add(self, name: str, factory: Callable[[encoding.Registry, dict], Action]):
        self.factories[name] = factory

    def create(self, name: str, er: encoding.Registry, opts: dict) -> Action:
        return self.factories[name](er, opts)
