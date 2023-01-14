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
from rcmt.source.gitea.client.models.pull_review_comment import PullReviewComment  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestPullReviewComment(unittest.TestCase):
    """PullReviewComment unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test PullReviewComment
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.pull_review_comment.PullReviewComment()  # noqa: E501
        if include_optional :
            return PullReviewComment(
                body = '', 
                commit_id = '', 
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                diff_hunk = '', 
                html_url = '', 
                id = 56, 
                original_commit_id = '', 
                original_position = 56, 
                path = '', 
                position = 56, 
                pull_request_review_id = 56, 
                pull_request_url = '', 
                resolver = rcmt.source.gitea.client.models.user.User(
                    active = True, 
                    avatar_url = '', 
                    created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    description = '', 
                    email = '', 
                    followers_count = 56, 
                    following_count = 56, 
                    full_name = '', 
                    id = 56, 
                    is_admin = True, 
                    language = '', 
                    last_login = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    location = '', 
                    login = '', 
                    login_name = 'empty', 
                    prohibit_login = True, 
                    restricted = True, 
                    starred_repos_count = 56, 
                    visibility = '', 
                    website = '', ), 
                updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                user = rcmt.source.gitea.client.models.user.User(
                    active = True, 
                    avatar_url = '', 
                    created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    description = '', 
                    email = '', 
                    followers_count = 56, 
                    following_count = 56, 
                    full_name = '', 
                    id = 56, 
                    is_admin = True, 
                    language = '', 
                    last_login = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    location = '', 
                    login = '', 
                    login_name = 'empty', 
                    prohibit_login = True, 
                    restricted = True, 
                    starred_repos_count = 56, 
                    visibility = '', 
                    website = '', )
            )
        else :
            return PullReviewComment(
        )

    def testPullReviewComment(self):
        """Test PullReviewComment"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
