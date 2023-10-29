# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io
import unittest
from unittest import mock

from rcmt.context import Context
from rcmt.filter import file_exists, line_in_file
from rcmt.source import Repository


class FileExistsTest(unittest.TestCase):
    def test_filter(self):
        repo = mock.Mock(spec=Repository)
        repo.has_file.return_value = True
        path = "test.json"

        result = file_exists(ctx=Context(repo), path=path)

        self.assertTrue(result)
        repo.has_file.assert_called_once_with(path)


class LineInFileTest(unittest.TestCase):
    def test_filter__does_match(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file.return_value = io.StringIO(
            """first line
second line
third line
"""
        )

        result = line_in_file(ctx=Context(repo), path="test.txt", search="second line")

        self.assertTrue(result)
        repo.get_file.assert_called_once_with("test.txt")

    def test_filter__does_not_match(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file.return_value = io.StringIO(
            """first line
second line
third line
"""
        )

        result = line_in_file(ctx=Context(repo), path="test.txt", search="other line")

        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")

    def test_filter__does_not_exist(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file = mock.Mock(side_effect=FileNotFoundError("does not exist"))

        result = line_in_file(ctx=Context(repo), path="test.txt", search="other line")

        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")
