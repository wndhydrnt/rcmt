import unittest

from rcmt.source import PullRequest


class PullRequestTest(unittest.TestCase):
    def test_custom(self):
        pr = PullRequest(
            "title_prefix", "title_body", "title_suffix", "custom_body", "custom_title"
        )

        self.assertEqual("custom_body", pr.body)
        self.assertEqual("custom_title", pr.title)

    def test_default(self):
        pr = PullRequest("title_prefix", "title_body", "title_suffix")
        pr.add_package("package1")
        pr.add_package("package2")

        want_body = """This update contains changes from the following packages:

- package1
- package2

---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._
"""
        self.assertEqual(want_body, pr.body)
        self.assertEqual("title_prefix title_body title_suffix", pr.title)
