# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import unittest
import unittest.mock

from rcmt.source import PullRequest, Repository
from rcmt.source.source import PullRequestComment


class PullRequestTest(unittest.TestCase):
    def test_custom(self):
        pr = PullRequest(
            True,
            False,
            "run_name",
            "title_prefix",
            "title_body",
            "title_suffix",
            "custom_body",
            "custom_title",
        )

        want_body = """custom_body

---

**Automerge:** Enabled. rcmt merges this automatically on its next run and if all checks have passed.  
**Ignore:** This PR will be recreated if closed.  

---
- [ ] If you want to rebase this PR, check this box
---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._"""
        self.assertEqual(want_body, pr.body)
        self.assertEqual("custom_title", pr.title)

    def test_default(self):
        pr = PullRequest(
            False, False, "run_name", "title_prefix", "title_body", "title_suffix"
        )

        want_body = """Apply changes from Run run_name

---

**Automerge:** Disabled. Merge this manually.  
**Ignore:** This PR will be recreated if closed.  

---
- [ ] If you want to rebase this PR, check this box
---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._"""
        self.assertEqual(want_body, pr.body)
        self.assertEqual("title_prefix title_body title_suffix", pr.title)

    def test_automerge_after(self):
        auto_merge_after = datetime.timedelta(days=2, hours=5)
        pr = PullRequest(
            True,
            False,
            "run_name",
            "title_prefix",
            "title_body",
            "title_suffix",
            auto_merge_after=auto_merge_after,
        )

        want_body = """Apply changes from Run run_name

---

**Automerge:** Enabled. rcmt automatically merges this in 2 days and if all checks have passed.  
**Ignore:** This PR will be recreated if closed.  

---
- [ ] If you want to rebase this PR, check this box
---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._"""

        self.assertEqual(want_body, pr.body)

    def test_merge_once(self):
        auto_merge_after = datetime.timedelta(days=2, hours=5)
        pr = PullRequest(
            True,
            True,
            "run_name",
            "title_prefix",
            "title_body",
            "title_suffix",
            auto_merge_after=auto_merge_after,
        )

        want_body = """Apply changes from Run run_name

---

**Automerge:** Enabled. rcmt automatically merges this in 2 days and if all checks have passed.  
**Ignore:** Close this PR and it will not be recreated again.  

---
- [ ] If you want to rebase this PR, check this box
---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._"""

        self.assertEqual(want_body, pr.body)


class RepositoryTest(unittest.TestCase):
    @unittest.mock.patch.object(Repository, "list_pr_comments")
    @unittest.mock.patch.object(Repository, "create_pr_comment")
    def test_create_pr_comment_with_identifier__comment_does_not_exist(
        self,
        create_pr_comment_mock: unittest.mock.Mock,
        list_pr_comments_mock: unittest.mock.Mock,
    ):
        pr_mock = unittest.mock.Mock()
        list_pr_comments_mock.return_value = []

        repo = Repository()
        repo.create_pr_comment_with_identifier(
            body="the comment", identifier="unit-test", pr=pr_mock
        )

        create_pr_comment_mock.assert_called_once_with(
            body="<!-- rcmt::unit-test -->\nthe comment", pr=pr_mock
        )

    @unittest.mock.patch.object(Repository, "list_pr_comments")
    @unittest.mock.patch.object(Repository, "create_pr_comment")
    def test_create_pr_comment_with_identifier__comment_already_exists(
        self,
        create_pr_comment_mock: unittest.mock.Mock,
        list_pr_comments_mock: unittest.mock.Mock,
    ):
        pr_mock = unittest.mock.Mock()
        pr_comment = PullRequestComment(
            body="<!-- rcmt::unit-test -->\nthe comment", id=123
        )
        list_pr_comments_mock.return_value = [pr_comment]

        repo = Repository()
        repo.create_pr_comment_with_identifier(
            body="the comment", identifier="unit-test", pr=pr_mock
        )

        create_pr_comment_mock.assert_not_called()

    @unittest.mock.patch.object(Repository, "list_pr_comments")
    @unittest.mock.patch.object(Repository, "delete_pr_comment")
    def test_delete_pr_comment_with_identifier(
        self,
        delete_pr_comment: unittest.mock.Mock,
        list_pr_comments_mock: unittest.mock.Mock,
    ):
        pr_mock = unittest.mock.Mock()
        pr_comment = PullRequestComment(
            body="<!-- rcmt::unit-test -->\nthe comment", id=123
        )
        list_pr_comments_mock.return_value = [pr_comment]

        repo = Repository()
        repo.delete_pr_comment_with_identifier(identifier="unit-test", pr=pr_mock)

        delete_pr_comment.assert_called_once_with(comment=pr_comment, pr=pr_mock)
