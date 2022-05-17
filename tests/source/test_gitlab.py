import unittest
import unittest.mock

import gitlab.exceptions
from gitlab.v4.objects import Project
from gitlab.v4.objects.files import ProjectFileManager

from rcmt.source.gitlab import GitlabRepository


class GitlabRepositoryTest(unittest.TestCase):
    def test_has_file__file_exists(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [
            {"path": "pyproject.toml", "type": "blob"}
        ]

        repo = GitlabRepository(project=project, url="")
        result = repo.has_file("pyproject.toml")

        self.assertTrue(result)
        project.repository_tree.assert_called_once_with(path="")

    def test_has_file__file_does_not_exist(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [{"path": "Pipenv", "type": "blob"}]

        repo = GitlabRepository(project=project, url="")
        result = repo.has_file("pyproject.toml")

        self.assertFalse(result)
        project.repository_tree.assert_called_once_with(path="")

    def test_has_file__wildcard(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [
            {"path": "production.json", "type": "blob"}
        ]

        repo = GitlabRepository(project=project, url="")
        result = repo.has_file("config/*.json")

        self.assertTrue(result)
        project.repository_tree.assert_called_once_with(path="config")
