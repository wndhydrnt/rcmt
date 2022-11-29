import io
import unittest
from unittest import mock

from rcmt.matcher import (
    And,
    Base,
    FileExists,
    FileNotExists,
    LineInFile,
    LineNotInFile,
    Not,
    Or,
)
from rcmt.source import Repository


class FileExistsTest(unittest.TestCase):
    def test_match(self):
        repo = mock.Mock(spec=Repository)
        repo.has_file.return_value = True
        path = "test.json"

        under_test = FileExists(path=path)
        result: bool = under_test.match(repo=repo)

        self.assertTrue(result)
        repo.has_file.assert_called_once_with(path)


class FileNotExistsTest(unittest.TestCase):
    def test_match(self):
        repo = mock.Mock(spec=Repository)
        repo.has_file.return_value = True
        path = "test.json"

        under_test = FileNotExists(path=path)
        result: bool = under_test.match(repo=repo)

        self.assertFalse(result)
        repo.has_file.assert_called_once_with(path)


class LineInFileTest(unittest.TestCase):
    def test_match__does_match(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file.return_value = io.StringIO(
            """first line
second line
third line
"""
        )
        under_test = LineInFile("test.txt", "second line")
        result = under_test.match(repo=repo)
        self.assertTrue(result)
        repo.get_file.assert_called_once_with("test.txt")

    def test_match__does_not_match(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file.return_value = io.StringIO(
            """first line
second line
third line
"""
        )
        under_test = LineInFile("test.txt", "other line")
        result = under_test.match(repo=repo)
        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")

    def test_match__does_not_exist(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file = mock.Mock(side_effect=FileNotFoundError("does not exist"))
        under_test = LineInFile("test.txt", "other line")
        result = under_test.match(repo=repo)
        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")


class LineNotInFileTest(unittest.TestCase):
    def test_match__line_in_file_exists(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file.return_value = io.StringIO(
            """first line
second line
third line
"""
        )
        under_test = LineNotInFile("test.txt", "second line")
        result = under_test.match(repo=repo)
        self.assertFalse(result)
        repo.get_file.assert_called_once_with("test.txt")

    def test_match__line_in_file_does_not_exists(self):
        repo = mock.Mock(spec=Repository)
        repo.get_file.return_value = io.StringIO(
            """first line
second line
third line
"""
        )
        under_test = LineNotInFile("test.txt", "fourth line")
        result = under_test.match(repo=repo)
        self.assertTrue(result)
        repo.get_file.assert_called_once_with("test.txt")


class MatcherMock(Base):
    def __init__(self, matches: bool):
        self.matches: bool = matches

    def match(self, repo: Repository) -> bool:
        return self.matches


class OrTest(unittest.TestCase):
    def test_match__does_match(self):
        mock1 = MatcherMock(matches=False)
        mock2 = MatcherMock(matches=True)

        under_test = Or(mock1, mock2)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertTrue(result)

    def test_match__does_not_match(self):
        mock1 = MatcherMock(matches=False)
        mock2 = MatcherMock(matches=False)

        under_test = Or(mock1, mock2)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertFalse(result)

    def test_init__no_args(self):
        with self.assertRaises(RuntimeError):
            Or()


class AndTest(unittest.TestCase):
    def test_match__does_match(self):
        mock1 = MatcherMock(matches=True)
        mock2 = MatcherMock(matches=True)

        under_test = And(mock1, mock2)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertTrue(result)

    def test_match__does_not_match(self):
        mock1 = MatcherMock(matches=True)
        mock2 = MatcherMock(matches=False)

        under_test = And(mock1, mock2)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertFalse(result)

    def test_init(self):
        with self.assertRaises(RuntimeError):
            And()


class NotTest(unittest.TestCase):
    def test_match(self):
        mmock = MatcherMock(matches=True)

        under_test = Not(mmock)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertFalse(result)
