import os
import tempfile
import unittest
from unittest import mock

from rcmt.package.action import Absent, DeleteKey, DeleteLineInFile, Exec, LineInFile


class AbsentTest(unittest.TestCase):
    def test_apply(self):
        with tempfile.TemporaryDirectory() as d:
            to_delete_path = os.path.join(d, "to_delete")
            with open(to_delete_path, "w+") as to_delete:
                to_delete.write("test")

            under_test = Absent("to_delete")
            under_test.apply(d, {})

            self.assertFalse(os.path.exists(to_delete_path))


class ExecTest(unittest.TestCase):
    @mock.patch("subprocess.run")
    @mock.patch("glob.iglob")
    def test_exec(self, glob_iglob: mock.MagicMock, subprocess_run: mock.MagicMock):
        completed_process = mock.Mock(returncode=1, stderr=b"stderr", stdout=b"stdout")
        subprocess_run.return_value = completed_process
        glob_iglob.return_value = ["/repo-checkout/afile"]
        ex = Exec(exec_path="/tmp/foo", selector="afile", timeout=120)
        with self.assertRaises(RuntimeError) as e:
            ex.apply("/repo-checkout", {})
        self.assertEqual(
            """Exec action call to /tmp/foo failed.
    stdout: stdout
    stderr: stderr""",
            str(e.exception),
        )


class DeleteKeysTest(unittest.TestCase):
    def test_process(self):
        data = {"foo": "bar", "level1": {"level2": {"level3": "foo"}}}
        key_to_delete = ["level1", "level2", "level3"]
        result = DeleteKey.process_recursive(key_to_delete, data)
        self.assertDictEqual({"foo": "bar", "level1": {"level2": {}}}, result)


class LineInFileTest(unittest.TestCase):
    def test_apply_line_does_not_exist(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("def\n")

            under_test = LineInFile("foobar", "test.txt")
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                lines = test_file.readlines()

            self.assertEqual(3, len(lines))
            self.assertEqual("foobar\n", lines[2])

    def test_apply_line_does_exist(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("foobar\n")
                test_file.write("def\n")

            under_test = LineInFile("foobar", "test.txt")
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                lines = test_file.readlines()

            self.assertEqual(3, len(lines))
            self.assertEqual("foobar\n", lines[1])


class DeleteLineInFileTest(unittest.TestCase):
    def test_apply_delete_line(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("foobar\n")
                test_file.write("def\n")

            under_test = DeleteLineInFile(line="foobar", selector="test.txt")
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                lines = test_file.readlines()

            self.assertEqual(2, len(lines))

    def test_apply_line_not_found(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("foo\n")
                test_file.write("def\n")

            under_test = DeleteLineInFile(line="bar", selector="test.txt")
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                lines = test_file.readlines()

            self.assertEqual(3, len(lines))
