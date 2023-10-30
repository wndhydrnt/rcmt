# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os
import platform
import tempfile
import unittest
from unittest import mock

from rcmt import context, fs
from rcmt.action import (
    absent,
    delete_line_in_file,
    exec,
    line_in_file,
    own,
    replace_in_line,
    seed,
)
from rcmt.source import source


class AbsentTest(unittest.TestCase):
    def test_apply__delete_file(self):
        with tempfile.TemporaryDirectory() as d:
            to_delete_path = os.path.join(d, "to_delete")
            with open(to_delete_path, "w+") as to_delete:
                to_delete.write("test")

            with fs.in_checkout_dir(d):
                absent("to_delete")

            self.assertFalse(os.path.exists(to_delete_path))

    def test_apply__delete_directory(self):
        with tempfile.TemporaryDirectory() as d:
            to_delete_path = os.path.join(d, "to_delete")
            os.mkdir(to_delete_path)

            with fs.in_checkout_dir(d):
                absent("to_delete")

            self.assertFalse(os.path.isdir(to_delete_path))


class ExecTest(unittest.TestCase):
    @mock.patch("subprocess.run")
    def test_exec(self, subprocess_run: mock.MagicMock):
        completed_process = mock.Mock(returncode=1, stderr=b"stderr", stdout=b"stdout")
        subprocess_run.return_value = completed_process
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError) as e:
                with fs.in_checkout_dir(d):
                    exec(executable="/tmp/foo", args=["--level", "error"], timeout=120)

            self.assertEqual(
                """Exec action call to /tmp/foo failed.
    stdout: stdout
    stderr: stderr""",
                str(e.exception),
            )
            # Workaround for macos symlink of /tmp to /private/tmp
            if platform.system() == "Darwin":
                cwd = f"/private{d}"
            else:
                cwd = d

            subprocess_run.assert_called_once_with(
                args=["/tmp/foo", "--level", "error"],
                capture_output=True,
                cwd=cwd,
                shell=False,
                timeout=120,
            )


class LineInFileTest(unittest.TestCase):
    def test_apply_line_does_not_exist(self):
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("def\n")

            with fs.in_checkout_dir(d):
                line_in_file(line="foobar", target="test.txt")

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

            with fs.in_checkout_dir(d):
                line_in_file(line="foobar", target="test.txt")

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

            with fs.in_checkout_dir(d):
                delete_line_in_file(search="foobar", target="test.txt")

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

            with fs.in_checkout_dir(d):
                delete_line_in_file(search="bar", target="test.txt")

            with open(test_file_path, "r") as test_file:
                lines = test_file.readlines()

            self.assertEqual(3, len(lines))


class OwnTest(unittest.TestCase):
    def test_apply(self):
        ctx = context.Context(repo=unittest.mock.Mock(spec=source.Repository))
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")

            with fs.in_checkout_dir(d):
                own(ctx=ctx, content="unit-test", target="test.txt")

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            self.assertEqual("unit-test", content)


class SeedTest(unittest.TestCase):
    def test_apply_seed_file(self):
        ctx = context.Context(repo=unittest.mock.Mock(spec=source.Repository))
        with tempfile.TemporaryDirectory() as d:
            with fs.in_checkout_dir(d):
                seed(ctx=ctx, content="unit-test", target="test.txt")

            with open(os.path.join(d, "test.txt"), "r") as test_file:
                content = test_file.read()

            self.assertEqual("unit-test", content)

    def test_apply_file_exists(self):
        ctx = context.Context(repo=unittest.mock.Mock(spec=source.Repository))
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")

            with fs.in_checkout_dir(d):
                seed(ctx=ctx, content="unit-test", target="test.txt")

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            self.assertEqual("abc\n", content)


class ReplaceInLineTest(unittest.TestCase):
    def test_apply_replace(self):
        ctx = context.Context(repo=unittest.mock.Mock(spec=source.Repository))
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("foo:bar:baz\n")
                test_file.write("def\n")

            with fs.in_checkout_dir(d):
                replace_in_line(
                    ctx=ctx,
                    search="(.+):bar:(.+)",
                    replace=r"\1:boom:\2",
                    target="test.txt",
                )

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            expected_content = """abc
foo:boom:baz
def
"""
            self.assertEqual(expected_content, content)

    def test_apply_templating(self):
        ctx = context.Context(repo=unittest.mock.Mock(spec=source.Repository))
        ctx.update_template_data(
            {
                "repo_source": "github.com",
                "repo_project": "wndhydrnt",
                "repo_name": "rcmt-test",
            }
        )
        with tempfile.TemporaryDirectory() as d:
            test_file_path = os.path.join(d, "test.txt")
            with open(test_file_path, "w+") as test_file:
                test_file.write("abc\n")
                test_file.write("github.com/wndhydrnt/rcmt-test-old\n")
                test_file.write("def\n")

            with fs.in_checkout_dir(d):
                replace_in_line(
                    ctx=ctx,
                    search="{{repo_source}}/{{repo_project}}/rcmt-test-old",
                    replace="{{repo_source}}/{{repo_project}}/{{repo_name}}",
                    target="test.txt",
                )

            with open(test_file_path, "r") as test_file:
                content = test_file.read()

            expected_content = """abc
github.com/wndhydrnt/rcmt-test
def
"""
            self.assertEqual(expected_content, content)
