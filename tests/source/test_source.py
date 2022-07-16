import datetime
import unittest

from rcmt.source import PullRequest


class PullRequestTest(unittest.TestCase):
    def test_custom(self):
        pr = PullRequest(
            True,
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
**Ignore:** Close this PR and it will not be recreated again.

---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._
"""
        self.assertEqual(want_body, pr.body)
        self.assertEqual("custom_title", pr.title)

    def test_default(self):
        pr = PullRequest(
            False, "run_name", "title_prefix", "title_body", "title_suffix"
        )

        want_body = """Apply changes from Run run_name

---

**Automerge:** Disabled. Merge this manually.
**Ignore:** Close this PR and it will not be recreated again.

---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._
"""
        self.assertEqual(want_body, pr.body)
        self.assertEqual("title_prefix title_body title_suffix", pr.title)

    def test_automerge_after(self):
        auto_merge_after = datetime.timedelta(days=2, hours=5)
        pr = PullRequest(
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

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._
"""

        self.assertEqual(want_body, pr.body)
