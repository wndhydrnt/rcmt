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
from rcmt.source.gitea.client.models.reference import Reference  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestReference(unittest.TestCase):
    """Reference unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Reference
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.reference.Reference()  # noqa: E501
        if include_optional :
            return Reference(
                object = rcmt.source.gitea.client.models.git_object_represents_a_git_object/.GitObject represents a Git object.(
                    sha = '', 
                    type = '', 
                    url = '', ), 
                ref = '', 
                url = ''
            )
        else :
            return Reference(
        )

    def testReference(self):
        """Test Reference"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()