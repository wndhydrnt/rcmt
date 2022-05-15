import json
import os
import tempfile
import unittest
from unittest import mock

from rcmt.encoding import Json, Registry
from rcmt.package.action import (
    Absent,
    DeleteKey,
    DeleteLineInFile,
    Exec,
    LineInFile,
    Merge,
    Own,
    ReplaceInLine,
    Seed,
)


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


class DeleteKeyTest(unittest.TestCase):
    def test_apply(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.json")
            test_file = open(test_file_path, "w+")
            data = {
                "root": {
                    "first_key": "first_value",
                    "second_key": "second_value",
                    "third_key": "third_value",
                }
            }
            json.dump(data, test_file)
            test_file.close()

            enc_registry = Registry()
            enc_registry.register(Json(), [".json"])
            under_test = DeleteKey("root.second_key", "test.json")
            under_test.encodings = enc_registry
            under_test.apply(d, {})

            with open(test_file_path, "r") as tf:
                data = json.load(tf)
                self.assertDictEqual(
                    {"root": {"first_key": "first_value", "third_key": "third_value"}},
                    data,
                )


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


class MergeTest(unittest.TestCase):
    def test_apply_strategy_replace(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.json")
            test_file = open(test_file_path, "w+")
            data = {"root": {"list": ["first_value", "second_value"]}}
            json.dump(data, test_file)
            test_file.close()

            enc_registry = Registry()
            enc_registry.register(Json(), [".json"])
            under_test = Merge(
                '{"root": { "list": ["first_value", "third_value"]}}', "test.json"
            )
            under_test.encodings = enc_registry
            under_test.apply(d, {})

            with open(test_file_path, "r") as tf:
                data = json.load(tf)
                self.assertDictEqual(
                    {"root": {"list": ["first_value", "third_value"]}},
                    data,
                )

    def test_apply_strategy_additive(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.json")
            test_file = open(test_file_path, "w+")
            data = {"root": {"list": ["first_value", "second_value"]}}
            json.dump(data, test_file)
            test_file.close()

            enc_registry = Registry()
            enc_registry.register(Json(), [".json"])
            under_test = Merge(
                '{"root": { "list": ["third_value"]}}',
                "test.json",
                merge_strategy="additive",
            )
            under_test.encodings = enc_registry
            under_test.apply(d, {})

            with open(test_file_path, "r") as tf:
                data = json.load(tf)
                self.assertDictEqual(
                    {"root": {"list": ["first_value", "second_value", "third_value"]}},
                    data,
                )


class OwnTest(unittest.TestCase):
    def test_apply(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")

            under_test = Own("unit-test", "test.txt")
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            self.assertEqual("unit-test", content)


class SeedTest(unittest.TestCase):
    def test_apply_seed_file(self):
        with tempfile.TemporaryDirectory() as d:
            under_test = Seed("unit-test", "test.txt")
            under_test.apply(d, {})

            with open(os.path.join(d, "test.txt"), "r") as test_file:
                content = test_file.read()

            self.assertEqual("unit-test", content)

    def test_apply_file_exists(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")

            under_test = Seed("unit-test", "test.txt")
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            self.assertEqual("abc\n", content)


class ReplaceInLineTest(unittest.TestCase):
    def test_apply_replace(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("foo:bar:baz\n")
                test_file.write("def\n")

            under_test = ReplaceInLine(
                search="(.+):bar:(.+)", replace=r"\1:boom:\2", selector="test.txt"
            )
            under_test.apply(d, {})

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            expected_content = """abc
foo:boom:baz
def
"""
            self.assertEqual(expected_content, content)

    def test_apply_templating(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("github.com/wndhydrnt/rcmt-test-old\n")
                test_file.write("def\n")

            under_test = ReplaceInLine(
                search="$repo_source/$repo_project/rcmt-test-old",
                replace="$repo_source/$repo_project/$repo_name",
                selector="test.txt",
            )
            under_test.apply(
                d,
                {
                    "repo_source": "github.com",
                    "repo_project": "wndhydrnt",
                    "repo_name": "rcmt-test",
                },
            )

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            expected_content = """abc
github.com/wndhydrnt/rcmt-test
def
"""
            self.assertEqual(expected_content, content)
