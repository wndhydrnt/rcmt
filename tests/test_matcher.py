# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io
import unittest
from unittest import mock

from rcmt.context import Context
from rcmt.matcher import And, Base, FileExists, LineInFile, Not, Or
from rcmt.source import Repository


class FileExistsTest(unittest.TestCase):
    def test_filter(self):
        repo = mock.Mock(spec=Repository)
        repo.has_file.return_value = True
        path = "test.json"

        under_test = FileExists(path=path)
        result = under_test.filter(Context(repo))

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
        under_test = LineInFile("test.txt", "second line")
        result = under_test.filter(Context(repo))
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
        under_test = LineInFile("test.txt", "other line")
        result = under_test.filter(Context(repo))
        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")

    def test_filter__does_not_exist(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file = mock.Mock(side_effect=FileNotFoundError("does not exist"))
        under_test = LineInFile("test.txt", "other line")
        result = under_test.filter(Context(repo))
        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")


class MatcherMock(Base):
    def __init__(self, matches: bool):
        self.matches: bool = matches

    def filter(self, ctx: Context) -> bool:
        return self.matches


class OrTest(unittest.TestCase):
    def test_filter__does_match(self):
        mock1 = MatcherMock(matches=False)
        mock2 = MatcherMock(matches=True)

        under_test = Or(mock1, mock2)
        result = under_test.filter(Context(mock.Mock(spec=Repository)))

        self.assertTrue(result)

    def test_filter__does_not_match(self):
        mock1 = MatcherMock(matches=False)
        mock2 = MatcherMock(matches=False)

        under_test = Or(mock1, mock2)
        result = under_test.filter(Context(mock.Mock(spec=Repository)))

        self.assertFalse(result)

    def test_init__no_args(self):
        with self.assertRaises(RuntimeError):
            Or()


class AndTest(unittest.TestCase):
    def test_filter__does_match(self):
        mock1 = MatcherMock(matches=True)
        mock2 = MatcherMock(matches=True)

        under_test = And(mock1, mock2)
        result = under_test.filter(Context(mock.Mock(spec=Repository)))

        self.assertTrue(result)

    def test_filter__does_not_match(self):
        mock1 = MatcherMock(matches=True)
        mock2 = MatcherMock(matches=False)

        under_test = And(mock1, mock2)
        result = under_test.filter(Context(mock.Mock(spec=Repository)))

        self.assertFalse(result)

    def test_init(self):
        with self.assertRaises(RuntimeError):
            And()


class NotTest(unittest.TestCase):
    def test_filter(self):
        mmock = MatcherMock(matches=True)

        under_test = Not(mmock)
        result = under_test.filter(Context(mock.Mock(spec=Repository)))

        self.assertFalse(result)
