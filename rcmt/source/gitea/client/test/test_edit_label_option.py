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
from rcmt.source.gitea.client.models.edit_label_option import EditLabelOption  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestEditLabelOption(unittest.TestCase):
    """EditLabelOption unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test EditLabelOption
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.edit_label_option.EditLabelOption()  # noqa: E501
        if include_optional :
            return EditLabelOption(
                color = '', 
                description = '', 
                name = ''
            )
        else :
            return EditLabelOption(
        )

    def testEditLabelOption(self):
        """Test EditLabelOption"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()