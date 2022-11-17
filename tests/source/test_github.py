import unittest
import unittest.mock

import github
import github.PullRequest
import github.Repository
from github.ContentFile import ContentFile
from github.GitRef import GitRef
from github.GitTree import GitTree
from github.GitTreeElement import GitTreeElement
from github.PullRequestPart import PullRequestPart

from rcmt.source import source
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

    def test_has_file__empty_repository(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        gh_repo.get_git_tree.side_effect = github.GithubException(
            status=409, data=None, headers={}
        )

        repo = GithubRepository(access_token="", repo=gh_repo)
        result = repo.has_file("pyroject.toml")

        self.assertFalse(result)

    def test_has_file__other_error(self):
        gh_repo = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo.default_branch = "main"
        gh_repo.get_git_tree.side_effect = github.GithubException(
            status=500, data=None, headers={}
        )

        repo = GithubRepository(access_token="", repo=gh_repo)
        with self.assertRaises(github.GithubException):
            repo.has_file("pyroject.toml")

    def test_close_pull_request(self):
        pr_mock = unittest.mock.Mock(spec=github.PullRequest.PullRequest)

        message = "Unit Test"
        repo = GithubRepository(
            access_token="", repo=unittest.mock.Mock(spec=github.Repository.Repository)
        )
        repo.close_pull_request(message, pr_mock)

        pr_mock.create_issue_comment.assert_called_once_with(body=message)
        pr_mock.edit.assert_called_once_with(state="closed")

    def test_update_pull_request__no_change(self):
        pr_data = source.PullRequest(False, False, "unit-test", "", "", "")
        pr_mock = unittest.mock.Mock(spec=github.PullRequest.PullRequest)
        pr_mock.title = pr_data.title
        pr_mock.body = pr_data.body

        repo = GithubRepository(
            access_token="", repo=unittest.mock.Mock(spec=github.Repository.Repository)
        )
        repo.update_pull_request(pr_mock, pr_data)

        pr_mock.edit.assert_not_called()

    def test_update_pull_request__has_changes(self):
        pr_data = source.PullRequest(False, False, "unit-test", "", "", "")
        pr_mock = unittest.mock.Mock(spec=github.PullRequest.PullRequest)
        pr_mock.title = "Old Title"
        pr_mock.body = "Old Body"

        repo = GithubRepository(
            access_token="", repo=unittest.mock.Mock(spec=github.Repository.Repository)
        )
        repo.update_pull_request(pr_mock, pr_data)

        pr_mock.edit.assert_called_once_with(title=pr_data.title, body=pr_data.body)

    def test_can_merge_pull_request__pr_mergeable(self):
        pr_mock = unittest.mock.Mock(spec=github.PullRequest.PullRequest)
        pr_mock.mergeable = None

        repo = GithubRepository(
            access_token="", repo=unittest.mock.Mock(spec=github.Repository.Repository)
        )
        result = repo.can_merge_pull_request(identifier=pr_mock)

        self.assertTrue(result)

    def test_can_merge_pull_request__pr_not_mergeable(self):
        pr_mock = unittest.mock.Mock(spec=github.PullRequest.PullRequest)
        pr_mock.mergeable = False

        repo = GithubRepository(
            access_token="", repo=unittest.mock.Mock(spec=github.Repository.Repository)
        )
        result = repo.can_merge_pull_request(identifier=pr_mock)

        self.assertFalse(result)

    def test_delete_branch__repo_configures_deletion(self):
        gh_repo_mock = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo_mock.delete_branch_on_merge = True

        repo = GithubRepository(access_token="", repo=gh_repo_mock)
        repo.delete_branch(
            identifier=unittest.mock.Mock(spec=github.PullRequest.PullRequest)
        )

        gh_repo_mock.get_git_ref.assert_not_called()

    def test_delete_branch__delete(self):
        git_ref_mock = unittest.mock.Mock(spec=GitRef)
        gh_repo_mock = unittest.mock.Mock(spec=github.Repository.Repository)
        gh_repo_mock.delete_branch_on_merge = False
        gh_repo_mock.get_git_ref.return_value = git_ref_mock
        pr_mock = unittest.mock.Mock(spec=github.PullRequest.PullRequest)
        head_mock = unittest.mock.Mock(spec=PullRequestPart)
        head_mock.ref = "rcmt/unittest"
        pr_mock.head = head_mock

        repo = GithubRepository(access_token="", repo=gh_repo_mock)
        repo.delete_branch(identifier=pr_mock)

        gh_repo_mock.get_git_ref.assert_called_once_with(ref="heads/rcmt/unittest")
        git_ref_mock.delete.assert_called_once_with()
