# coding: utf-8

"""
    Gitea API.

    This documentation describes the Gitea API.  # noqa: E501

    The version of the OpenAPI document: 1.18.0+1
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import rcmt.source.gitea.client
from rcmt.source.gitea.client.models.edit_repo_option import EditRepoOption  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestEditRepoOption(unittest.TestCase):
    """EditRepoOption unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test EditRepoOption
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.edit_repo_option.EditRepoOption()  # noqa: E501
        if include_optional :
            return EditRepoOption(
                allow_manual_merge = True, 
                allow_merge_commits = True, 
                allow_rebase = True, 
                allow_rebase_explicit = True, 
                allow_rebase_update = True, 
                allow_squash_merge = True, 
                archived = True, 
                autodetect_manual_merge = True, 
                default_branch = '', 
                default_delete_branch_after_merge = True, 
                default_merge_style = '', 
                description = '', 
                enable_prune = True, 
                external_tracker = rcmt.source.gitea.client.models.external_tracker.ExternalTracker(
                    external_tracker_format = '', 
                    external_tracker_regexp_pattern = '', 
                    external_tracker_style = '', 
                    external_tracker_url = '', ), 
                external_wiki = rcmt.source.gitea.client.models.external_wiki.ExternalWiki(
                    external_wiki_url = '', ), 
                has_issues = True, 
                has_projects = True, 
                has_pull_requests = True, 
                has_wiki = True, 
                ignore_whitespace_conflicts = True, 
                internal_tracker = rcmt.source.gitea.client.models.internal_tracker.InternalTracker(
                    allow_only_contributors_to_track_time = True, 
                    enable_issue_dependencies = True, 
                    enable_time_tracker = True, ), 
                mirror_interval = '', 
                name = '', 
                private = True, 
                template = True, 
                website = ''
            )
        else :
            return EditRepoOption(
        )

    def testEditRepoOption(self):
        """Test EditRepoOption"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
