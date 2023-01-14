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
from rcmt.source.gitea.client.models.git_hook import GitHook  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestGitHook(unittest.TestCase):
    """GitHook unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test GitHook
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.git_hook.GitHook()  # noqa: E501
        if include_optional :
            return GitHook(
                content = '', 
                is_active = True, 
                name = ''
            )
        else :
            return GitHook(
        )

    def testGitHook(self):
        """Test GitHook"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()