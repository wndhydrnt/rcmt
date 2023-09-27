import io
import os
import pathlib
import re
import shutil
import string
import subprocess
import tempfile
from typing import Optional, Union

import mergedeep

from rcmt import encoding, util
from rcmt.fs import FileProxy, read_file_or_str


class Action:
    """Action is the abstract class that defines the interface each action implements."""

    def __call__(self, repo_path: str, tpl_data: dict) -> None:
        return self.apply(repo_path=repo_path, tpl_data=tpl_data)

    def __repr__(self) -> str:
        return self.__class__.__name__

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        """apply modifies files in the clone of a repository.

        Args:
            repo_path: The absolute path to the file in a repository to modify.
            tpl_data: The content of the file from an Action, already populated with
                      template data.

        Changes:
            - 0.5.0: Parameter `pkg_path` removed.
        """
        raise NotImplementedError("class does not implement Action.apply()")


class GlobMixin:
    """GlobMixin simplifies working with glob selectors.

    Classes that extend GlobMixin do not need to implement calls to `glob` from stdlib.
    Instead, a class implements `process_file()` to process each file that matches the
    glob selector.

    Args:
        selector: A glob selector.
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
    """Deletes a file or directory.

    Args:
        target: Path to the file or directory to delete.

    Example:
        ```python
        # Delete the file config.yaml at the root of a repository.
        Absent(target="config.yaml")
        ```
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
    """Own ensures that a file in a repository stays the same.

    It overwrites the content of the file with the data passed to this Action.

    Args:
        content: Content of the file to write.
        target: Path to the file in a repository to own.

    Example:
        ```python
        # Ensure that .flake8 looks the same across all repositories.
        content = "[flake8]\\nmax-line-length = 88\\nextend-ignore = E203"
        Own(content=content, target=".flake8")
        ```

    Changes:
        0.5.0: Parameter `content` added. Parameter `source` removed.

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
    """Seed ensures that a file in a repository is present.

    It does not modify the file again if the file is present in a repository.

    Args:
        content: Path to the file in a repository to seed.
        target: A string or path to a file that contain the content to seed.

    Example:
        ```python
        # Ensure that the default Makefile is present.
        Seed(content="foo:\n\t# foo", target="Makefile")
        ```

    Changes:
        0.5.0: Parameter `content` added. Parameter `source` removed.

    """

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        repo_file_path = os.path.join(repo_path, self.target)
        if os.path.isfile(repo_file_path):
            return

        super().apply(repo_path, tpl_data)


class EncodingAware:
    def __init__(self) -> None:
        self._encodings: encoding.Registry

    @property
    def encodings(self) -> encoding.Registry:
        return self._encodings

    @encodings.setter
    def encodings(self, er: encoding.Registry):
        self._encodings = er


class Merge(Action, EncodingAware):
    """Merge merges the content of a file in a repository with the content set in this
    Action.

    It supports merging of various file formats through :doc:`encoding`.

    Args:
        content: The raw content to merge.
        selector: Glob selector to find the files to merge.
        merge_strategy: Strategy to use when merging data. `replace` replaces a key
                        if it already exists. `additive` combines collections, e.g.
                        `list` or `set`.

    Example:
        ```python
        # Ensure that pyproject.toml contains specific keys.
        Merge(selector="pyproject.toml", source="pyproject.toml")
        ```

    Changes:
        0.5.0: Parameter `content` added. Parameter `source` removed.
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
    """Delete a key in a file. The file has to be in a format supported by encoding.

    Args:
        key: Path to the key in the data structure.
        target: Path to the file to modify.

    Example:
        ```python
        # Delete key "bar" in dict "foo" in file config.json.
        DeleteKey(key="foo.bar", target="config.json")
        ```
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


class Exec(Action):
    """Exec calls an executable with the given arguments. The executable can then modify
    files. A common use case are code formatters such as black, prettier or "go fmt".

    The current working directory is set to the checkout of a repository.

    This Action expects the executable it calls to have been installed already. It does
    not install the executable.

    Args:
        executable: Path to the executable.
        args: List of arguments to pass to the executable.
        timeout: Maximum runtime of the executable, in seconds.

    Example:
        ```python
        # Let black format all files in the current directory. The current directory is
        # the checkout of a repository.
        Exec(executable="black", args=["--line-length", "120", "."])
        ```
    """

    def __init__(
        self,
        executable: str,
        args: Optional[list[str]] = None,
        timeout: int = 120,
    ):
        self.args: list[str] = args if args else []
        self.executable = executable
        self.timeout = timeout

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        result = subprocess.run(
            args=[self.executable] + self.args,
            capture_output=True,
            cwd=repo_path,
            shell=False,
            timeout=self.timeout,
        )
        if result.returncode > 0:
            raise RuntimeError(
                f"""Exec action call to {self.executable} failed.
    stdout: {result.stdout.decode('utf-8')}
    stderr: {result.stderr.decode('utf-8')}"""
            )


class LineInFile(GlobMixin, Action):
    """LineInFile ensures that a line exists in a file. It adds the line if it does not
    exist.

    Args:
        line: Line to search for.
        selector: Glob selector to find the files to modify.

    Example:
        ```python
        LineInFile(line="The Line", selector="file.txt")
        ```
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
    """DeleteLineInFile deletes a line in a file if the file contains the line.

    Args:
        line: Line to search for. This is a regular expression.
        selector: Glob selector to find the files to modify.

    Example:
        ```python
        DeleteLineInFile(line="The Line", selector="file.txt")
        ```

    Changes:
        - 0.5.0: Does not wrap parameter `line` with `^` and `$` characters anymore.
        - 0.5.0: Does not apply `strip()` to each line read of a file.
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
    """ReplaceInLine iterates over each line of a file and replaces a string if it
    matches a regular expression.

    It uses `re.sub()`.

    Args:
        search: Pattern to search for. This is a regular expression.
        replace: Replacement if `search` matches.
        selector: Glob selector to find the files to modify.
        flags: Additional flags passed to `re.sub()`.

    Example:
        ```python
        # Turns the line "This is a test." into "This is an example."
        ReplaceInLine(
            search="a test",
            replace=r"an example",
            selector="file.txt",
            flags=re.IGNORECASE
        )
        ```

    Both `search` and `replace` parameters support `Templating`_.

    Note:
        Make sure to escape every `$` in a regular expression with `$$` to avoid errors
        like `Invalid placeholder in string: line 1, col 43`.

        ❌ **Don't**: `^github.com/wndhydrnt/rcmt$`

        ✅ **Do**: `^github.com/wndhydrnt/rcmt$$`
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
