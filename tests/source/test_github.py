import unittest
import unittest.mock

import github
import github.Repository

from rcmt.source.github import GithubRepository


class GithubRepositoryTest(unittest.TestCase):
    def test_has_file__file_exists(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        # Return value actually does not matter here.
        gh_repo.get_contents.return_value = object()

        repo = GithubRepository(repo=gh_repo)
        result = repo.has_file("pyroject.toml")

        self.assertTrue(result)
        gh_repo.get_contents.assert_called_once_with(path="pyroject.toml", ref="main")

    def test_has_file__file_does_not_exist(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        gh_repo.get_contents.side_effect = github.UnknownObjectException(404, {}, {})

        repo = GithubRepository(repo=gh_repo)
        result = repo.has_file("pyroject.toml")

        self.assertFalse(result)
        gh_repo.get_contents.assert_called_once_with(path="pyroject.toml", ref="main")

    def test_has_file__other_error(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        gh_repo.get_contents.side_effect = github.UnknownObjectException(500, {}, {})

        repo = GithubRepository(repo=gh_repo)
        with self.assertRaises(github.UnknownObjectException):
            repo.has_file("pyroject.toml")

        gh_repo.get_contents.assert_called_once_with(path="pyroject.toml", ref="main")
