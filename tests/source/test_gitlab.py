import unittest
import unittest.mock

import gitlab.exceptions
from gitlab.v4.objects import Project
from gitlab.v4.objects.files import ProjectFileManager

from rcmt.source.gitlab import GitlabRepository


class GitlabRepositoryTest(unittest.TestCase):
    def test_has_file__file_exists(self):
        files = unittest.mock.Mock(spec=ProjectFileManager)
        # Return value actually does not matter here.
        files.get.return_value = object()
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.files = files

        repo = GitlabRepository(project=project, url="")
        result = repo.has_file("pyproject.toml")

        self.assertTrue(result)
        files.get.assert_called_once_with(file_path="pyproject.toml", ref="main")

    def test_has_file__file_does_not_exist(self):
        files = unittest.mock.Mock(spec=ProjectFileManager)
        files.get.side_effect = gitlab.exceptions.GitlabGetError(response_code=404)
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.files = files

        repo = GitlabRepository(project=project, url="")
        result = repo.has_file("pyproject.toml")

        self.assertFalse(result)
        files.get.assert_called_once_with(file_path="pyproject.toml", ref="main")

    def test_has_file__other_error(self):
        files = unittest.mock.Mock(spec=ProjectFileManager)
        files.get.side_effect = gitlab.exceptions.GitlabGetError(response_code=500)
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.files = files

        repo = GitlabRepository(project=project, url="")
        with self.assertRaises(gitlab.exceptions.GitlabGetError):
            repo.has_file("pyproject.toml")

        files.get.assert_called_once_with(file_path="pyproject.toml", ref="main")
