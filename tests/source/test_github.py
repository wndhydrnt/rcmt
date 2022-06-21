import unittest
import unittest.mock

import github
import github.Repository
from github.ContentFile import ContentFile
from github.GitTree import GitTree
from github.GitTreeElement import GitTreeElement

from rcmt.source.github import GithubRepository


class GithubRepositoryTest(unittest.TestCase):
    def test_get_file__file_exists(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        file = unittest.mock.Mock(spec=ContentFile)
        file.decoded_content = b"abc"
        gh_repo.get_contents.return_value = file

        repo = GithubRepository(access_token="", repo=gh_repo)
        result = repo.get_file("text.txt")

        self.assertEqual("abc", result.read())
        gh_repo.get_contents.assert_called_once_with(path="text.txt", ref="main")

    def test_get_file__file_exists_list(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        file = unittest.mock.Mock(spec=ContentFile)
        file.decoded_content = b"abc"
        gh_repo.get_contents.return_value = [file]

        repo = GithubRepository(access_token="", repo=gh_repo)
        result = repo.get_file("text.txt")

        self.assertEqual("abc", result.read())

    def test_get_file__file_does_not_exist(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        gh_repo.get_contents = unittest.mock.Mock(
            side_effect=github.UnknownObjectException(
                data=None, headers=None, status=404
            )
        )

        repo = GithubRepository(access_token="", repo=gh_repo)

        with self.assertRaises(FileNotFoundError):
            repo.get_file("text.txt")

    def test_has_file__file_exists(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        tree_mock = unittest.mock.Mock(spec=GitTree)
        tree_element_mock = unittest.mock.Mock(spec=GitTreeElement)
        tree_element_mock.path = "pyroject.toml"
        tree_mock.tree = [tree_element_mock]
        gh_repo.get_git_tree.return_value = tree_mock

        repo = GithubRepository(access_token="", repo=gh_repo)
        result = repo.has_file("pyroject.toml")

        self.assertTrue(result)
        gh_repo.get_git_tree.assert_called_once_with("main", True)

    def test_has_file__file_does_not_exist(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        tree_mock = unittest.mock.Mock(spec=GitTree)
        tree_mock.tree = []
        gh_repo.get_git_tree.return_value = tree_mock

        repo = GithubRepository(access_token="", repo=gh_repo)
        result = repo.has_file("pyroject.toml")

        self.assertFalse(result)
        gh_repo.get_git_tree.assert_called_once_with("main", True)

    def test_has_file__wildcard(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        tree_mock = unittest.mock.Mock(spec=GitTree)
        tree_element_mock = unittest.mock.Mock(spec=GitTreeElement)
        tree_element_mock.path = "pyroject.toml"
        tree_mock.tree = [tree_element_mock]
        gh_repo.get_git_tree.return_value = tree_mock

        repo = GithubRepository(access_token="", repo=gh_repo)
        result = repo.has_file("*.toml")

        self.assertTrue(result)
        gh_repo.get_git_tree.assert_called_once_with("main", True)
