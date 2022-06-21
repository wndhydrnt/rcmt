import io
import unittest
from unittest import mock

from rcmt.matcher import LineInFile
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
