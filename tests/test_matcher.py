import io
import unittest
from unittest import mock

from rcmt.matcher import Base, LineInFile, Or
from rcmt.source import Repository


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


class OrTest(unittest.TestCase):
    class ActionMock(Base):
        def __init__(self, matches: bool):
            self.matches: bool = matches

        def match(self, repo: Repository) -> bool:
            return self.matches

    def test_match__does_match(self):
        mock1 = self.ActionMock(matches=False)
        mock2 = self.ActionMock(matches=True)

        under_test = Or(mock1, mock2)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertTrue(result)

    def test_match__does_not_match(self):
        mock1 = self.ActionMock(matches=False)
        mock2 = self.ActionMock(matches=False)

        under_test = Or(mock1, mock2)
        result = under_test.match(repo=mock.Mock(spec=Repository))

        self.assertFalse(result)

    def test_init__no_args(self):
        with self.assertRaises(RuntimeError):
            Or()
