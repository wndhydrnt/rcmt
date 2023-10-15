# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import unittest

from rcmt.task import Task, TaskRegistry, read, registry


class ReadTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        registry.task_path = None
        registry.tasks = []

    def test_read(self):
        read("tests/fixtures/test_run/ReadTaskTest/test_read/task.py")
        self.assertEqual(1, len(registry.tasks))
        t = registry.tasks[0]

        for fp in t.file_proxies:
            self.assertEqual("tests/fixtures/test_run/ReadTaskTest/test_read", fp.path)

    def test_read__code_exception(self):
        with self.assertRaises(RuntimeError) as e:
            read(
                "tests/fixtures/test_run/ReadTaskTest/test_read__code_exception/task.py"
            )

        self.assertEqual(
            "Import failed with KeyError: 'key'",
            str(e.exception),
        )


class TaskTest(unittest.TestCase):
    def test_branch__custom_name_not_altered(self):
        r = Task(name="This is a test", branch_name="feature/branch-name")
        result = r.branch("rcmt/")
        self.assertEqual("feature/branch-name", result)

    def test_branch__slugify_default(self):
        r = Task(name="This is a test")
        result = r.branch("rcmt/")
        self.assertEqual("rcmt/this-is-a-test", result)


class TaskRegistryTest(unittest.TestCase):
    def test_register__task_path_not_set(self):
        tr = TaskRegistry()
        with self.assertRaises(RuntimeError) as e:
            tr.register(task=Task(name="unit-test"))

        self.assertEqual(
            str(e.exception),
            "Task path must be set during task registration",
        )

    def test_register__task_register_twice(self):
        tr = TaskRegistry()
        tr.task_path = "tests/fixtures/test_run/ReadTaskTest/test_read/task.py"
        t = Task(name="unit-test")
        tr.register(t)

        with self.assertRaises(RuntimeError) as e:
            tr.register(task=t)

        self.assertEqual(str(e.exception), "Task 'unit-test' already registered")
