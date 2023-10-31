# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import unittest
from unittest import mock

from rcmt.task import Task, TaskRegistry, TaskWrapper, read, registry


class ReadTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        registry.task_path = None
        registry.tasks = []

    def test_read(self):
        read("tests/fixtures/test_run/ReadTaskTest/test_read/task.py")
        self.assertEqual(1, len(registry.tasks), "Should register the task")
        t = registry.tasks[0]
        self.assertEqual("unit-test", t.name, "Should register the expected task")

    def test_read__code_exception(self):
        with self.assertRaises(RuntimeError) as e:
            read(
                "tests/fixtures/test_run/ReadTaskTest/test_read__code_exception/task.py"
            )

        self.assertEqual(
            "Import failed with KeyError: 'key'",
            str(e.exception),
        )

    def test_read__not_registered(self):
        with self.assertRaises(RuntimeError) as e:
            read("tests/fixtures/test_task/test_read__not_registered/task.py")

        self.assertEqual(
            "Import failed with RuntimeError: File 'tests/fixtures/test_task/test_read__not_registered/task.py' defines Task 'Test' but does not register it - use rcmt.register_task(Test())",
            str(e.exception),
        )


class TaskWrapperTest(unittest.TestCase):
    def test_branch__custom_name_not_altered(self):
        task = mock.Mock(spec=Task)
        task.name = "This is a test"
        task.branch_name = "feature/branch-name"

        wrapper = TaskWrapper(t=task)
        result = wrapper.branch("rcmt/")

        self.assertEqual(
            "feature/branch-name", result, "Should use the name set by the task"
        )

    def test_branch__slugify_default(self):
        task = mock.Mock(spec=Task)
        task.name = "This is a test"
        task.branch_name = ""

        wrapper = TaskWrapper(t=task)
        result = wrapper.branch("rcmt/")

        self.assertEqual(
            "rcmt/this-is-a-test",
            result,
            "Should concat prefix and slugified name of task",
        )


class TaskRegistryTest(unittest.TestCase):
    def test_register__task_path_not_set(self):
        tr = TaskRegistry()
        t = mock.Mock(spec=Task)
        t.name = "uni-test"

        tr.register(task=t)

        self.assertEqual(0, len(tr.tasks), "List of registered tasks should be empty")

    def test_register__task_register_twice(self):
        tr = TaskRegistry()
        tr.task_path = "tests/fixtures/test_run/ReadTaskTest/test_read/task.py"
        t = mock.Mock(spec=Task)
        t.name = "unit-test"
        tr.register(t)

        with self.assertRaises(RuntimeError) as e:
            tr.register(task=t)

        self.assertEqual(str(e.exception), "Task 'unit-test' already registered")
