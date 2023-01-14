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
from rcmt.source.gitea.client.models.edit_branch_protection_option import EditBranchProtectionOption  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestEditBranchProtectionOption(unittest.TestCase):
    """EditBranchProtectionOption unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test EditBranchProtectionOption
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.edit_branch_protection_option.EditBranchProtectionOption()  # noqa: E501
        if include_optional :
            return EditBranchProtectionOption(
                approvals_whitelist_teams = [
                    ''
                    ], 
                approvals_whitelist_username = [
                    ''
                    ], 
                block_on_official_review_requests = True, 
                block_on_outdated_branch = True, 
                block_on_rejected_reviews = True, 
                dismiss_stale_approvals = True, 
                enable_approvals_whitelist = True, 
                enable_merge_whitelist = True, 
                enable_push = True, 
                enable_push_whitelist = True, 
                enable_status_check = True, 
                merge_whitelist_teams = [
                    ''
                    ], 
                merge_whitelist_usernames = [
                    ''
                    ], 
                protected_file_patterns = '', 
                push_whitelist_deploy_keys = True, 
                push_whitelist_teams = [
                    ''
                    ], 
                push_whitelist_usernames = [
                    ''
                    ], 
                require_signed_commits = True, 
                required_approvals = 56, 
                status_check_contexts = [
                    ''
                    ], 
                unprotected_file_patterns = ''
            )
        else :
            return EditBranchProtectionOption(
        )

    def testEditBranchProtectionOption(self):
        """Test EditBranchProtectionOption"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
