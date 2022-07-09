import unittest
import unittest.mock

import gitlab.exceptions
from gitlab.v4.objects import (
    Project,
    ProjectMergeRequest,
    ProjectMergeRequestNoteManager,
)
from gitlab.v4.objects.files import ProjectFile, ProjectFileManager

from rcmt.source.gitlab import GitlabRepository


class GitlabRepositoryTest(unittest.TestCase):
    def test_get_file__file_exists(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        content = "abc".encode("utf-8")
        file = unittest.mock.Mock(spec=ProjectFile)
        file.decode.return_value = content
        file_manager = unittest.mock.Mock(spec=ProjectFileManager)
        file_manager.get.return_value = file
        project.files = file_manager

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.get_file(path="text.txt")

        self.assertEqual("abc", result.read())
        file_manager.get.assert_called_once_with(file_path="text.txt", ref="main")

    def test_get_file__file_does_not_exists(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        file_manager = unittest.mock.Mock(spec=ProjectFileManager)
        file_manager.get = unittest.mock.Mock(side_effect=gitlab.GitlabGetError)
        project.files = file_manager

        repo = GitlabRepository(project=project, token="", url="")

        with self.assertRaises(FileNotFoundError):
            repo.get_file(path="text.txt")

    def test_get_file__unable_to_decode(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.namespace = {"full_path": "wandhydrant/test"}
        project.path = "test"
        file = unittest.mock.Mock(spec=ProjectFile)
        file.decode.return_value = None
        file_manager = unittest.mock.Mock(spec=ProjectFileManager)
        file_manager.get.return_value = file
        project.files = file_manager

        repo = GitlabRepository(project=project, token="", url="")

        with self.assertRaises(FileNotFoundError):
            repo.get_file(path="text.txt")

    def test_has_file__file_exists(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [
            {"path": "pyproject.toml", "type": "blob"}
        ]

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("pyproject.toml")

        self.assertTrue(result)
        project.repository_tree.assert_called_once_with(path="")

    def test_has_file__file_does_not_exist(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [{"path": "Pipenv", "type": "blob"}]

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("pyproject.toml")

        self.assertFalse(result)
        project.repository_tree.assert_called_once_with(path="")

    def test_has_file__wildcard(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [
            {"path": "production.json", "type": "blob"}
        ]

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("config/*.json")

        self.assertTrue(result)
        project.repository_tree.assert_called_once_with(path="config")

    def test_close_pull_request(self):
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        notes_mock = unittest.mock.Mock(spec=ProjectMergeRequestNoteManager)
        pr_mock.notes = notes_mock

        message = "Unit Test"
        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        repo.close_pull_request(message, pr_mock)

        notes_mock.create.assert_called_once_with({"body": message})
        self.assertEqual("close", pr_mock.state_event)
        pr_mock.save.assert_called_once_with()
