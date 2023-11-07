# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import tempfile
from typing import Optional
from unittest import TestCase

from rcmt import Context
from rcmt.fs import in_checkout_dir
from rcmt.source import Repository as BaseRepository
from rcmt.task import Task


class File:
    """File emulates a file in a repository.

    Args:
        content: The content of the file.
        path: The path of the file, relative to the root of the repository.
    """

    def __init__(self, content: str, path: str):
        self._content = content
        self._path = path

    @property
    def content(self) -> str:
        """content is a getter method.

        Returns:
            The content of the File.
        """
        return self._content

    @property
    def path(self) -> str:
        """path is a getter method.

        Returns:
            The path of the File.
        """
        return self._path


class Repository(BaseRepository):
    """Repository emulates a repository as hosted by a source code host.

    It implements the methods of rcmt.source.Repository necessary to make tests work.

    Args:
        name: The name of the repository to emulate, e.g. github.com/wndhydrnt/rcmt.
        files: Zero or more Files to add to the repository.
    """

    def __init__(self, name: str, *files: File):
        self._full_name = name
        self._name_parts = name.split("/")

        self._files: list[File] = list(files)

    def add_file(self, f: File) -> None:
        """add_file adds a File to the known files of the repository.

        Args:
            f: The File to add.

        """
        self._files.append(f)

    def has_file(self, path: str) -> bool:
        """has_file implements rcmt.source.Repository"""
        for file in self._files:
            if file.path == path:
                return True

        return False

    @property
    def files(self) -> list[File]:
        """files is a getter method.

        Returns:
            All files of the repository.
        """
        return self._files

    @property
    def name(self) -> str:
        return self._name_parts[-1]

    @property
    def project(self) -> str:
        return "/".join(self._name_parts[1:-1])

    @property
    def source(self) -> str:
        return self._name_parts[0]

    @staticmethod
    def from_directory(name: str, path: str) -> "Repository":
        """from_directory creates a new Repository from a directory.

        Args:
            name: The name of the repository to emulate, e.g. github.com/wndhydrnt/rcmt.
            path: The path to the directory from which to read the files.

        Returns:
            An instance of Repository.
        """
        if os.path.isdir(path) is False:
            raise RuntimeError(f"path '{path}' is not a directory")

        repo = Repository(name=name)
        for root, dirs, files in os.walk(path):
            for raw_file in files:
                p = os.path.join(root, raw_file)
                with open(p) as f:
                    content = f.read()

                path_in_repo = os.path.join(root.removeprefix(path), raw_file)
                file = File(content=content, path=path_in_repo)
                repo.add_file(file)

        return repo


class TaskTestCase(TestCase):
    """TaskTestCase is the base class unit tests of Tasks should inherit.

    It provides methods that simplify writing tests for a Task.
    """

    def _assertRepositoryEqual(self, first: Repository, second: Repository):
        self.assertEqual(first=first.full_name, second=second.full_name)
        for expected_file in first.files:
            actual_file = self._find_file(files=second.files, search=expected_file)
            if actual_file is None:
                self.fail(f"Expected file '{expected_file.path}' does not exist")
            else:
                self.assertMultiLineEqual(
                    expected_file.content,
                    actual_file.content,
                    f"Content of '{expected_file.path}' not equal",
                )

    def assertTaskModifiesRepository(
        self, task: Task, before: Repository, after: Repository
    ):
        """assertTaskModifiesRepository validates that a Task has modified a repository.

        It works by
        1. Recreate the repository in a temporary directory from `before`.
        2. Execute the `apply()` method of the given `task`.
        3. Compare the files and contents in the temporary directory with the expected
           state as described by `after`.

        Args:
            task: The Task to test.
            before: The repository in the state before any modifications by the Task
                    have been applied.
            after: The repository in the expected state after the Task has modified it.
        """
        ctx = Context(repo=before)
        with tempfile.TemporaryDirectory() as d:
            for f in before.files:
                temp_file_path = os.path.join(d, f.path)
                dirname = os.path.dirname(temp_file_path)
                os.makedirs(name=dirname, exist_ok=True)
                with open(temp_file_path, "w+") as temp_file:
                    temp_file.write(f.content)

            with in_checkout_dir(d):
                task.apply(ctx=ctx)

            result = Repository.from_directory(name=before.full_name, path=d)
            self._assertRepositoryEqual(after, result)

    def assertTaskFilterMatches(self, task: Task, repo: Repository):
        """assertTaskFilterMatches validates that a Task matches a repository.

        Args:
            task: The Task to test.
            repo: The repository to test against.
        """
        ctx = Context(repo=repo)
        result = task.filter(ctx)
        self.assertTrue(
            result, f"Filter of Task '{task.name} does not match repository"
        )

    def assertTaskFilterDoesNotMatch(self, task: Task, repo: Repository):
        """assertTaskFilterDoesNotMatch validates that a Task does not match a
        repository.

        Args:
            task: The Task to test.
            repo: The repository to test against.
        """
        ctx = Context(repo=repo)
        result = task.filter(ctx)
        self.assertFalse(
            result,
            f"Filter of Task '{task.name}' matches repository '{repo.full_name}' but should not",
        )

    @staticmethod
    def _find_file(files: list[File], search: File) -> Optional[File]:
        for f in files:
            if f.path == search.path:
                return f

        return None
