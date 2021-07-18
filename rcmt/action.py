"""
Actions encapsulate behavior of how to change a file.
"""
import glob
import io
import os
import pathlib
import string
import subprocess
from typing import Callable

from rcmt import encoding, manifest


class Action:
    """
    Action is the abstract class that defines the interface each action implements.
    """

    def apply(self, repo_file_path: str, tpl_data: dict) -> None:
        """
        apply modifies a file in a repository.

        :param repo_file_path: The absolute path to the file in a repository to modify.
        :param tpl_data: The content of the file from a package, already populated with
                         template data.
        :return: None
        """
        raise NotImplementedError("class does not implement Action.apply()")


class Absent(Action):
    def __init__(self, target):
        self.target = target

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.exists(repo_file_path):
            os.remove(repo_file_path)


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

    def __init__(self, target: str, tpl: string.Template):
        self.tpl = tpl
        self.target = target

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        file_path = os.path.join(repo_path, self.target)
        with open(file_path, "w+") as f:
            f.write(self.tpl.substitute(tpl_data))


def own_factory(er: encoding.Registry, opts: manifest.Action, pkg_path: str) -> Own:
    assert opts.own is not None
    source_path = os.path.join(pkg_path, opts.own.source)
    with open(source_path, "r") as f:
        data = f.read()

    return Own(opts.own.target, string.Template(data))


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

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.isfile(repo_file_path):
            return

        super().apply(repo_file_path, tpl_data)


def seed_factory(er: encoding.Registry, opts: manifest.Action, pkg_path: str) -> Seed:
    assert opts.seed is not None
    source_path = os.path.join(pkg_path, opts.seed.source)
    with open(source_path, "r") as f:
        data = f.read()

    return Seed(opts.seed.target, string.Template(data))


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

    def __init__(
        self, encodings: encoding.Registry, selector: str, source_data: string.Template
    ):
        self.encodings = encodings
        self.selector = selector
        self.source_data = source_data

    @staticmethod
    def factory(er: encoding.Registry, opts: manifest.Action, pkg_path: str):
        assert opts.merge is not None
        source_path = os.path.join(pkg_path, opts.merge.source)
        with open(source_path, "r") as f:
            data = f.read()

        return Merge(er, opts.merge.selector, string.Template(data))

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        paths = glob.iglob(os.path.join(repo_path, self.selector), recursive=True)
        for p in paths:
            ext = pathlib.Path(p).suffix
            enc = self.encodings.get_for_extension(ext)
            with open(p, "r") as f:
                orig_data = enc.decode(f)

            tpl = enc.decode(io.StringIO(self.source_data.substitute(tpl_data)))
            merged_data = enc.merge(orig_data, tpl)
            with open(p, "w") as f:
                enc.encode(f, merged_data)


class DeleteKey(Action):
    """
    DeleteKey deletes a key from a dictionary.

    **Usage**

    .. code-block:: yaml

       name: delete_keys_example
       actions:
         - action: delete_key
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

    def __init__(self, encodings: encoding.Registry, key_path: list[str], target: str):
        self.encodings = encodings
        self.key_path = key_path
        self.target = target

    @staticmethod
    def factory(er: encoding.Registry, opts: manifest.Action, pkg_path: str):
        assert opts.delete_key is not None
        return DeleteKey(er, opts.delete_key.key.split("."), opts.delete_key.target)

    def apply(self, repo_path: str, tpl_data: dict) -> None:
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

    def __init__(self, exec_path: str, selector: str, timeout: int):
        self.exec_path = exec_path
        self.selector = selector
        self.timeout = timeout

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        repo_file_paths = glob.iglob(os.path.join(repo_path, self.selector))
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


def exec_factory(er: encoding.Registry, opts: manifest.Action, pkg_path: str) -> Exec:
    assert opts.exec is not None
    return Exec(opts.exec.path, opts.exec.selector, opts.exec.timeout)


class Registry:
    def __init__(self):
        self.factories: dict[
            str, Callable[[encoding.Registry, manifest.Action, str], Action]
        ] = {}

    def add(
        self,
        name: str,
        factory: Callable[[encoding.Registry, manifest.Action, str], Action],
    ):
        self.factories[name] = factory

    def create(
        self, name: str, er: encoding.Registry, opts: manifest.Action, pkg_path: str
    ) -> Action:
        return self.factories[name](er, opts, pkg_path)
