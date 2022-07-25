import io
import os
import pathlib
import re
import shutil
import string
import subprocess
import tempfile
from typing import Union

import mergedeep

from rcmt import encoding, util
from rcmt.fs import FileProxy, read_file_or_str


class Action:
    """
    Action is the abstract class that defines the interface each action implements.
    """

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        """
        apply modifies a file in a repository.

        :param repo_path: The absolute path to the file in a repository to modify.
        :param tpl_data: The content of the file from an Action, already populated with
                         template data.
        :return: None

        .. versionchanged:: 0.5.0
           Parameter ``pkg_path`` removed.
        """
        raise NotImplementedError("class does not implement Action.apply()")


class GlobMixin:
    """
    GlobMixin simplifies working with glob selectors.

    Classes that extend GlobMixin do not need to implement calls to ``glob`` from stdlib.
    Instead, a class implements ``process_file()`` to process each file that matches the
    glob selector.
    """

    def __init__(self, selector: str):
        self.selector = selector

    def apply(self, repo_path: str, tpl_data: dict):
        repo_file_paths = util.iglob(repo_path, self.selector)
        for repo_file_path in repo_file_paths:
            self.process_file(repo_file_path, tpl_data)

    def process_file(self, path: str, tpl_data: dict):
        raise NotImplementedError("Action does not implement GlobMixin.process_file()")


class Absent(Action):
    """
    Deletes a file or directory.

    :param target: Path to the file or directory to delete.

    **Example**

    .. code-block:: python

       # Delete the file config.yaml at the root of a repository.
       Absent(target="config.yaml")
    """

    def __init__(self, target: str):
        self.target = target

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.isfile(repo_file_path):
            os.remove(repo_file_path)
            return

        if os.path.isdir(repo_file_path):
            shutil.rmtree(repo_file_path)


class Own(Action):
    """
    Own ensures that a file in a repository stays the same.

    It always overwrites the data in the file with the data from this Action.

    :param content: Content of the file to write.
    :param target: Path to the file in a repository to own.

    **Example**

    .. code-block:: python

       # Ensure that .flake8 looks the same across all repositories.
       content = "[flake8]\\nmax-line-length = 88\\nextend-ignore = E203"
       Own(content=content, target=".flake8")

    .. versionchanged:: 0.5.0
       Parameter ``content`` added. Parameter ``source`` removed.
    """

    def __init__(self, content: Union[str, FileProxy], target: str):
        self.content = content
        self.target = target

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        content = read_file_or_str(self.content)
        file_path = os.path.join(repo_path, self.target)
        with open(file_path, "w+") as f:
            f.write(string.Template(content).substitute(tpl_data))


class Seed(Own):
    """
    Seed ensures that a file in a repository is present.

    It does not modify the file again if the file is present in a repository.

    :param target: Path to the file in a repository to seed.
    :param source: A string or path to a file that contain the content to seed.

    **Example**

    .. code-block:: python

       # Ensure that the default Makefile is present.
       Seed(content="foo:\n\t# foo", target="Makefile")

    .. versionchanged:: 0.5.0
       Parameter ``content`` added. Parameter ``source`` removed.
    """

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.isfile(repo_file_path):
            return

        super().apply(repo_path, tpl_data)


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
    """
    Merge merges the content of a file in a repository with the content set in this
    Action.

    It supports merging of various file formats through :doc:`encoding`.

    :param selector: Glob selector to find the files to merge.
    :param source: Path to the file that contains the source data.
    :param merge_strategy: Strategy to use when merging data. ``replace`` replaces a
                           key if it already exists. ``additive`` combines collections,
                           e.g. ``list`` or ``set``.

    **Example**

    .. code-block:: python

       # Ensure that pyproject.toml contains specific keys.
       Merge(selector="pyproject.toml", source="pyproject.toml")

    .. versionchanged:: 0.5.0
       Parameter ``content`` added. Parameter ``source`` removed.
    """

    def __init__(
        self,
        content: Union[str, FileProxy],
        selector: str,
        merge_strategy: str = "replace",
    ):
        super().__init__()
        self.content = content
        self.selector = selector
        self.strategy = mergedeep.Strategy.REPLACE
        if merge_strategy == "additive":
            self.strategy = mergedeep.Strategy.ADDITIVE

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        content = read_file_or_str(self.content)
        data = string.Template(content).substitute(tpl_data)
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
    """
    Delete a key in a file. The file has to be in a format supported by :doc:`encoding`.

    :param key: Path to the key in the data structure.
    :param target: Path to the file to modify.

    **Example**

    .. code-block:: python

       # Delete key "bar" in dict "foo" in file config.json.
       DeleteKey(key="foo.bar", target="config.json")
    """

    def __init__(self, key: str, target: str):
        super().__init__()
        self.key_path = key.split(".")
        self.target = target

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


class Exec(GlobMixin, Action):
    """
    Exec calls an executable and passes matching files in a repository to it. The
    executable can then modify each file.

    The executable should expect the path of a file as its only positional argument.

    :param exec_path: Path to the executable.
    :param selector: Glob selector to find the files to modify.
    :param timeout: Maximum runtime of the executable, in seconds.

    **Example**

    .. code-block:: python

       # Find all Python files in a repository recursively and pass each path to /opt/the-binary.
       Exec(exec_path="/opt/the-binary", selector="**/*.py")
    """

    def __init__(self, exec_path: str, selector: str, timeout: int = 120):
        super(Exec, self).__init__(selector)

        self.exec_path = exec_path
        self.timeout = timeout

    def process_file(self, path: str, tpl_data: dict):
        result = subprocess.run(
            args=[self.exec_path, path],
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


class LineInFile(GlobMixin, Action):
    """
    LineInFile ensures that a line exists in a file. It adds the line if it does not exist.

    :param line: Line to search for.
    :param selector: Glob selector to find the files to modify.

    **Example**

    .. code-block:: python

       LineInFile(line="The Line", selector="file.txt")
    """

    def __init__(self, line: str, selector: str):
        super(LineInFile, self).__init__(selector)

        self.line = line.strip()

    def process_file(self, path: str, tpl_data: dict):
        with open(path, "r") as f:
            for line in f:
                if line.strip() == self.line:
                    return None

        with open(path, "a") as f:
            f.write(self.line)
            f.write("\n")


class DeleteLineInFile(GlobMixin, Action):
    """
    DeleteLineInFile deletes a line in a file if the file contains the line.

    :param line: Line to search for. This is a regular expression.
    :param selector: Glob selector to find the files to modify.

    **Example**

    .. code-block:: python

       DeleteLineInFile(line="The Line", selector="file.txt")

    .. versionchanged:: 0.5.0
       Does not wrap parameter ``line`` with ``^`` and ``$`` characters anymore.

    .. versionchanged:: 0.5.0
       Does not apply ``strip()`` to each line read from a file.
    """

    def __init__(self, line: str, selector: str):
        super().__init__(selector)
        self.regex = re.compile(line)

    def process_file(self, path: str, tpl_data: dict):
        with open(path, "r") as f:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmpf:
                tmp_file_path = tmpf.name
                line_deleted = False
                for line in f:
                    if self.regex.search(line) is None:
                        tmpf.write(line)
                    else:
                        line_deleted = True

        if line_deleted:
            shutil.move(tmp_file_path, path)


class ReplaceInLine(GlobMixin, Action):
    """
    ReplaceInLine iterates over each line of a file and replaces a string if it matches
    a regular expression.

    It uses ``re.sub()``.

    :param search: Pattern to search for. This is a regular expression.
    :param replace: Replacement if ``search`` matches.
    :param selector: Glob selector to find the files to modify.
    :param flags: Additional flags passed to ``re.sub()``.

    **Example**

    .. code-block:: python

       # Turns the line "This is a test." into "This is an example."
       ReplaceInLine(
           search="a test",
           replace=r"an example",
           selector="file.txt",
           flags=re.IGNORECASE
       )

    Both ``search`` and ``replace`` parameters support `Templating`_.

    .. note::
       Make sure to escape every ``$`` in a regular expression with ``$$`` to avoid
       errors like ``Invalid placeholder in string: line 1, col 43``.

       **Don't**

       ``^github.com/wndhydrnt/rcmt$``

       **Do**

       ``^github.com/wndhydrnt/rcmt$$``

    .. versionadded:: 0.6.0
    """

    def __init__(self, search: str, replace: str, selector: str, flags: int = 0):
        super(ReplaceInLine, self).__init__(selector)
        self.search = string.Template(search)
        self.replace = string.Template(replace)
        self.flags = flags

    def process_file(self, path: str, tpl_data: dict):
        search = self.search.substitute(tpl_data)
        replace = self.replace.substitute(tpl_data)
        with open(path, "r") as f:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmpf:
                for line in f:
                    tmpf.write(re.sub(search, replace, line, flags=self.flags))

        shutil.move(tmpf.name, path)
