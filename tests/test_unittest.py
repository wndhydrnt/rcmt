# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os

from rcmt import Context, Task
from rcmt.unittest import File, Repository, TaskTestCase


class UnitTestTaskComplex(Task):
    name = "unit-test-task"

    def filter(self, ctx: Context) -> bool:
        return ctx.repo.full_name.startswith(
            "github.com/wndhydrnt/"
        ) and ctx.repo.has_file("test.json")

    def apply(self, ctx: Context) -> None:
        with open("test.json", "w+") as f:
            json.dump({"abc": "def"}, f)

        os.remove("level1/level2/delete.txt")


class UnitTestTaskSimple(Task):
    def filter(self, ctx: Context) -> bool:
        return True

    def apply(self, ctx: Context) -> None:
        with open("test.txt", "w+") as f:
            f.write("TEST\n")


class TestTaskTestCase(TaskTestCase):
    def test_assertTaskFilterMatches(self):
        repo = Repository(
            "github.com/wndhydrnt/rcmt", File(content="{}", path="test.json")
        )

        task = UnitTestTaskComplex()

        self.assertTaskFilterMatches(task=task, repo=repo)

    def test_assertTaskFilterDoesNotMatch(self):
        repo = Repository("github.com/wndhydrnt/rcmt")

        task = UnitTestTaskComplex()

        self.assertTaskFilterDoesNotMatch(task=task, repo=repo)

    def test_assertTaskModifiesRepository(self):
        repo_before = Repository(
            "github.com/wndhydrnt/rcmt", File(content="{}", path="test.json")
        )
        repo_before.add_file(File(content="", path="level1/level2/delete.txt"))

        repo_after = Repository(
            "github.com/wndhydrnt/rcmt",
            File(content=json.dumps({"abc": "def"}), path="test.json"),
        )

        task = UnitTestTaskComplex()

        self.assertTaskModifiesRepository(
            task=task, before=repo_before, after=repo_after
        )

    def test_assertTaskModifiesRepository_from_directory(self):
        repo_before = Repository.from_directory(
            name="unittest", path="tests/fixtures/test_unittest/before"
        )
        repo_after = Repository.from_directory(
            name="unittest", path="tests/fixtures/test_unittest/after"
        )

        task = UnitTestTaskSimple()

        self.assertTaskModifiesRepository(
            task=task, before=repo_before, after=repo_after
        )
