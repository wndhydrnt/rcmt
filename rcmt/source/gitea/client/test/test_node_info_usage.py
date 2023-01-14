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
from rcmt.source.gitea.client.models.node_info_usage import NodeInfoUsage  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestNodeInfoUsage(unittest.TestCase):
    """NodeInfoUsage unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test NodeInfoUsage
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.node_info_usage.NodeInfoUsage()  # noqa: E501
        if include_optional :
            return NodeInfoUsage(
                local_comments = 56, 
                local_posts = 56, 
                users = rcmt.source.gitea.client.models.node_info_usage_users.NodeInfoUsageUsers(
                    active_halfyear = 56, 
                    active_month = 56, 
                    total = 56, )
            )
        else :
            return NodeInfoUsage(
        )

    def testNodeInfoUsage(self):
        """Test NodeInfoUsage"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()