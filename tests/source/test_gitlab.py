# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import types
import unittest
import unittest.mock

import gitlab.exceptions
from gitlab.v4.objects import (
    CurrentUser,
    MergeRequest,
    MergeRequestManager,
    Project,
    ProjectBranch,
    ProjectBranchManager,
    ProjectMergeRequest,
    ProjectMergeRequestApproval,
    ProjectMergeRequestApprovalManager,
    ProjectMergeRequestManager,
    ProjectMergeRequestNote,
    ProjectMergeRequestNoteManager,
)
from gitlab.v4.objects.files import ProjectFile, ProjectFileManager
from gitlab.v4.objects.projects import ProjectManager

from rcmt.source import source
from rcmt.source.gitlab import Gitlab, GitlabRepository
from rcmt.source.source import PullRequestComment


class GitlabRepositoryTest(unittest.TestCase):
    def test_create_pull_request(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.namespace = {"full_path": "rcmt"}
        project.path = "unit-test"
        project_merge_request_manager = unittest.mock.Mock(
            spec=ProjectMergeRequestManager
        )
        project.mergerequests = project_merge_request_manager
        pr_data = source.PullRequest(
            auto_merge=False,
            merge_once=False,
            run_name="unit-test",
            title_prefix="",
            title_body="",
            title_suffix="",
            custom_body="body",
            custom_title="title",
            labels=["abc", "def"],
        )

        repo = GitlabRepository(project=project, token="", url="")
        repo.create_pull_request(branch="rcmt/unit-test", pr=pr_data)

        body = """body

---

**Automerge:** Disabled. Merge this manually.  
**Ignore:** This PR will be recreated if closed.  

---
- [ ] If you want to rebase this PR, check this box
---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._"""
        project_merge_request_manager.create.assert_called_once_with(
            {
                "description": body,
                "labels": ["abc", "def"],
                "source_branch": "rcmt/unit-test",
                "target_branch": "main",
                "title": "title",
            }
        )

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
        project.repository_tree.assert_called_once_with(path="", iterator=True)

    def test_has_file__nested(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [
            {"path": "data/config/test.json", "type": "blob"}
        ]

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("data/config/test.json")

        self.assertTrue(result)
        project.repository_tree.assert_called_once_with(
            path="data/config", iterator=True
        )

    def test_has_file__file_does_not_exist(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [{"path": "Pipenv", "type": "blob"}]

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("pyproject.toml")

        self.assertFalse(result)
        project.repository_tree.assert_called_once_with(path="", iterator=True)

    def test_has_file__wildcard(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.return_value = [
            {"path": "config/production.json", "type": "blob"}
        ]

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("config/*.json")

        self.assertTrue(result)
        project.repository_tree.assert_called_once_with(path="config", iterator=True)

    def test_has_file__empty_repository(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.namespace = {"full_path": "wandhydrant/test"}
        project.path = "test"
        project.repository_tree.side_effect = gitlab.GitlabGetError(response_code=404)

        repo = GitlabRepository(project=project, token="", url="")
        result = repo.has_file("config/*.json")

        self.assertFalse(result)

    def test_has_file__other_gitlab_error(self):
        project = unittest.mock.Mock(spec=Project)
        project.default_branch = "main"
        project.repository_tree.side_effect = gitlab.GitlabGetError(response_code=500)

        repo = GitlabRepository(project=project, token="", url="")
        with self.assertRaises(gitlab.GitlabGetError):
            repo.has_file("config/*.json")

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

    def test_create_pr_comment(self):
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        notes_mock = unittest.mock.Mock(spec=ProjectMergeRequestNoteManager)
        pr_mock.notes = notes_mock

        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        repo.create_pr_comment(body="Unit Test", pr=pr_mock)

        notes_mock.create.assert_called_once_with({"body": "Unit Test"})

    def test_update_pull_request__no_change(self):
        pr_data = source.PullRequest(False, False, "unit-test", "", "", "")
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        pr_mock.title = pr_data.title
        pr_mock.description = pr_data.body

        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        repo.update_pull_request(pr_mock, pr_data)

        pr_mock.save.assert_not_called()

    def test_update_pull_request__has_changes(self):
        pr_data = source.PullRequest(False, False, "unit-test", "", "", "")
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        pr_mock.title = "Old Title"
        pr_mock.description = "Old Body"
        project_mock = unittest.mock.Mock(spec=Project)
        project_mock.namespace = {"full_path": "wandhydrant/test"}
        project_mock.path = "test"

        repo = GitlabRepository(project=project_mock, token="", url="")
        repo.update_pull_request(pr_mock, pr_data)

        self.assertEqual(pr_data.title, pr_mock.title)
        self.assertEqual(pr_data.body, pr_mock.description)
        pr_mock.save.assert_called_once()

    def test_has_successful_pr_build__missing_approvals(self):
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        approval_manager_mock = unittest.mock.Mock(
            spec=ProjectMergeRequestApprovalManager
        )
        pr_mock.approvals = approval_manager_mock
        mr_approval_mock = unittest.mock.Mock(spec=ProjectMergeRequestApproval)
        mr_approval_mock.approved = False
        approval_manager_mock.get.return_value = mr_approval_mock
        project_mock = unittest.mock.Mock(spec=Project)
        project_mock.namespace = {"full_path": "wandhydrant/test"}
        project_mock.path = "test"

        repo = GitlabRepository(project=project_mock, token="", url="")
        result = repo.has_successful_pr_build(identifier=pr_mock)

        self.assertFalse(result)

    def test_pr_created_at__parses_timestamp(self):
        mr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        mr_mock.created_at = "2022-08-02T16:07:26.697Z"

        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        result = repo.pr_created_at(mr_mock)

        self.assertEqual(
            result,
            datetime.datetime(
                year=2022,
                month=8,
                day=2,
                hour=16,
                minute=7,
                second=26,
                microsecond=697000,
                tzinfo=datetime.timezone.utc,
            ),
        )

    def test_can_merge_pull_request(self):
        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        self.assertTrue(
            repo.can_merge_pull_request(unittest.mock.Mock(spec=ProjectMergeRequest))
        )

    def test_delete_branch__remove_branch_configured(self):
        branches_mock = unittest.mock.Mock(spec=ProjectBranchManager)
        project_mock = unittest.mock.Mock(spec=Project)
        project_mock.branches = branches_mock
        mr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        mr_mock.should_remove_source_branch = True

        repo = GitlabRepository(project=project_mock, token="", url="")
        repo.delete_branch(identifier=mr_mock)

        branches_mock.get.assert_not_called()

    def test_delete_branch__delete(self):
        branch_mock = unittest.mock.Mock(spec=ProjectBranch)
        branches_mock = unittest.mock.Mock(spec=ProjectBranchManager)
        branches_mock.get.return_value = branch_mock
        project_mock = unittest.mock.Mock(spec=Project)
        project_mock.branches = branches_mock
        mr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        mr_mock.should_remove_source_branch = False
        mr_mock.source_branch = "rcmt/unittest"

        repo = GitlabRepository(project=project_mock, token="", url="")
        repo.delete_branch(identifier=mr_mock)

        branches_mock.get.assert_called_once_with(id="rcmt/unittest", lazy=True)
        branch_mock.delete.assert_called_once_with()

    def test_list_pr_comments(self):
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        notes_mock = unittest.mock.Mock(spec=ProjectMergeRequestNoteManager)
        note_one = unittest.mock.Mock(spec=ProjectMergeRequestNote)
        note_one.body = "Note 1"
        note_one.id = 123
        note_two = unittest.mock.Mock(spec=ProjectMergeRequestNote)
        note_two.body = "Note 2"
        note_two.id = 456
        notes_mock.list.return_value = [note_one, note_two]
        pr_mock.notes = notes_mock

        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        result = list(repo.list_pr_comments(pr_mock))

        self.assertListEqual(
            result,
            [
                PullRequestComment(body="Note 1", id=123),
                PullRequestComment(body="Note 2", id=456),
            ],
        )

    def test_delete_pr_comment(self):
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        notes_mock = unittest.mock.Mock(spec=ProjectMergeRequestNoteManager)
        pr_mock.notes = notes_mock
        comment = PullRequestComment(body="comment", id=123)

        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        repo.delete_pr_comment(comment=comment, pr=pr_mock)

        notes_mock.delete.assert_called_once_with(comment.id)

    def test_get_pr_body(self):
        pr_mock = unittest.mock.Mock(spec=ProjectMergeRequest)
        pr_mock.description = "comment body"

        repo = GitlabRepository(
            project=unittest.mock.Mock(spec=Project), token="", url=""
        )
        result = repo.get_pr_body(pr_mock)

        self.assertEqual("comment body", result)


class GitlabTest(unittest.TestCase):
    def test_create_from_name__return_repository(self):
        project_mock = unittest.mock.Mock(spec=Project)
        projects_mock = unittest.mock.Mock(spec=ProjectManager)
        projects_mock.get.return_value = project_mock
        client_mock = unittest.mock.Mock(spec=gitlab.Gitlab)
        client_mock.private_token = "private_token"
        client_mock.projects = projects_mock

        gl = Gitlab(url="http://localhost", private_token=client_mock.private_token)
        gl.client = client_mock
        result = gl.create_from_name("localhost/group/subgroup/project")

        self.assertIsInstance(result, GitlabRepository)
        projects_mock.get.assert_called_once_with(id="group/subgroup/project")

    def test_create_from_name__not_matching_host(self):
        projects_mock = unittest.mock.Mock(spec=ProjectManager)
        client_mock = unittest.mock.Mock(spec=gitlab.Gitlab)
        client_mock.private_token = "private_token"
        client_mock.projects = projects_mock

        gl = Gitlab(url="http://localhost", private_token=client_mock.private_token)
        gl.client = client_mock
        result = gl.create_from_name("other/group/project")

        self.assertIsNone(result)
        projects_mock.get.assert_not_called()

    def test_create_from_name__project_not_found(self):
        projects_mock = unittest.mock.Mock(spec=ProjectManager)
        projects_mock.get.side_effect = gitlab.GitlabGetError
        client_mock = unittest.mock.Mock(spec=gitlab.Gitlab)
        client_mock.private_token = "private_token"
        client_mock.projects = projects_mock

        gl = Gitlab(url="http://localhost", private_token=client_mock.private_token)
        gl.client = client_mock
        result = gl.create_from_name("localhost/group/subgroup/project")

        self.assertIsNone(result)
        projects_mock.get.assert_called_once_with(id="group/subgroup/project")

    def test_list_repositories(self):
        now = datetime.datetime.now()
        project_mock = unittest.mock.Mock(spec=Project)
        projects_mock = unittest.mock.Mock(spec=ProjectManager)
        projects_mock.list.return_value = [project_mock]
        client_mock = unittest.mock.Mock(spec=gitlab.Gitlab)
        client_mock.private_token = "private_token"
        client_mock.projects = projects_mock

        gl = Gitlab(url="http://localhost", private_token=client_mock.private_token)
        gl.client = client_mock
        result = gl.list_repositories(since=now)

        self.assertIsInstance(result, types.GeneratorType)
        result_list = list(result)
        self.assertEqual(1, len(result_list))
        self.assertIsInstance(result_list[0], GitlabRepository)
        gl_repo = result_list[0]
        if isinstance(gl_repo, GitlabRepository):
            self.assertEqual(gl_repo._project, project_mock)
            self.assertEqual(gl_repo.token, client_mock.private_token)
            self.assertEqual(gl_repo.url, "localhost")

        projects_mock.list.assert_called_once_with(
            archived=False, last_activity_after=now, iterator=True, min_access_level=30
        )

    def test_list_repositories_with_open_pull_requests(self):
        client_mock = unittest.mock.Mock(spec=gitlab.Gitlab)
        client_mock.private_token = "private_token"
        client_mock.user = None

        user_mock = unittest.mock.Mock(spec=CurrentUser)
        user_mock.attributes = {"id": 123}

        def auth_call():
            client_mock.user = user_mock

        client_mock.auth = auth_call

        first_merge_request_mock = unittest.mock.Mock(spec=MergeRequest)
        first_merge_request_mock.project_id = 456
        second_merge_request_mock = unittest.mock.Mock(spec=MergeRequest)
        second_merge_request_mock.project_id = 456
        mergerequests_mock = unittest.mock.Mock(spec=MergeRequestManager)
        mergerequests_mock.list.return_value = [
            first_merge_request_mock,
            second_merge_request_mock,
        ]
        client_mock.mergerequests = mergerequests_mock

        project_mock = unittest.mock.Mock(spec=Project)
        project_mock.archived = False
        projects_mock = unittest.mock.Mock(spec=ProjectManager)
        projects_mock.get.return_value = project_mock
        client_mock.projects = projects_mock

        gl = Gitlab(url="http://localhost", private_token=client_mock.private_token)
        gl.client = client_mock
        result = list(gl.list_repositories_with_open_pull_requests())

        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], GitlabRepository)
        gl_repo = result[0]
        if isinstance(gl_repo, GitlabRepository):
            self.assertEqual(gl_repo._project, project_mock)
            self.assertEqual(gl_repo.token, client_mock.private_token)
            self.assertEqual(gl_repo.url, "localhost")

        mergerequests_mock.list.assert_called_once_with(
            author_id=123, iterator=True, state="opened"
        )
        projects_mock.get.assert_called_once_with(id=456)

    def test_list_repositories_with_open_pull_requests__archived_repository(self):
        client_mock = unittest.mock.Mock(spec=gitlab.Gitlab)
        client_mock.private_token = "private_token"
        client_mock.user = None

        user_mock = unittest.mock.Mock(spec=CurrentUser)
        user_mock.attributes = {"id": 123}

        def auth_call():
            client_mock.user = user_mock

        client_mock.auth = auth_call

        merge_request_mock = unittest.mock.Mock(spec=MergeRequest)
        merge_request_mock.project_id = 456
        mergerequests_mock = unittest.mock.Mock(spec=MergeRequestManager)
        mergerequests_mock.list.return_value = [merge_request_mock]
        client_mock.mergerequests = mergerequests_mock

        project_mock = unittest.mock.Mock(spec=Project)
        project_mock.archived = True
        project_mock.path_with_namespace = "unit/test"
        projects_mock = unittest.mock.Mock(spec=ProjectManager)
        projects_mock.get.return_value = project_mock
        client_mock.projects = projects_mock

        gl = Gitlab(url="http://localhost", private_token=client_mock.private_token)
        gl.client = client_mock
        result = list(gl.list_repositories_with_open_pull_requests())

        self.assertEqual(0, len(result))
        mergerequests_mock.list.assert_called_once_with(
            author_id=123, iterator=True, state="opened"
        )
        projects_mock.get.assert_called_once_with(id=456)
