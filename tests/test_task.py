import unittest

from rcmt.task import Task, read


class ReadTaskTest(unittest.TestCase):
    def test_read(self):
        r = read("tests/fixtures/test_run/ReadTaskTest/test_read/task.py")
        for fp in r.file_proxies:
            self.assertEqual("tests/fixtures/test_run/ReadTaskTest/test_read", fp.path)

    def test_read_invalid_type(self):
        with self.assertRaises(RuntimeError) as e:
            read("tests/fixtures/test_run/ReadTaskTest/test_read_invalid_type/task.py")

        self.assertEqual(
            "Task file tests/fixtures/test_run/ReadTaskTest/test_read_invalid_type/task.py defines variable 'task' but is not of type Task",
            str(e.exception),
        )

    def test_read_task_var_not_exists(self):
        with self.assertRaises(RuntimeError) as e:
            read(
                "tests/fixtures/test_run/ReadTaskTest/test_read_run_var_not_exists/task.py"
            )

        self.assertEqual(
            "Task file tests/fixtures/test_run/ReadTaskTest/test_read_run_var_not_exists/task.py does not define variable 'task'",
            str(e.exception),
        )

    def test_read__backward_compatible_run_var(self):
        r = read(
            "tests/fixtures/test_run/ReadTaskTest/test_read__backward_compatible_run_var/run.py"
        )


class RunTest(unittest.TestCase):
    def test_branch__slugify_custom_name(self):
        r = Task(name="This is a test", branch_name="Branch Name")
        result = r.branch("rcmt/")
        self.assertEqual("branch-name", result)

    def test_branch__slugify_default(self):
        r = Task(name="This is a test")
        result = r.branch("rcmt/")
        self.assertEqual("rcmt/this-is-a-test", result)
