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
from rcmt.source.gitea.client.models.repo_transfer import RepoTransfer  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestRepoTransfer(unittest.TestCase):
    """RepoTransfer unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test RepoTransfer
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.repo_transfer.RepoTransfer()  # noqa: E501
        if include_optional :
            return RepoTransfer(
                doer = rcmt.source.gitea.client.models.user.User(
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
                recipient = rcmt.source.gitea.client.models.user.User(
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
                teams = [
                    rcmt.source.gitea.client.models.team.Team(
                        can_create_org_repo = True, 
                        description = '', 
                        id = 56, 
                        includes_all_repositories = True, 
                        name = '', 
                        organization = rcmt.source.gitea.client.models.organization.Organization(
                            avatar_url = '', 
                            description = '', 
                            full_name = '', 
                            id = 56, 
                            location = '', 
                            name = '', 
                            repo_admin_change_team_access = True, 
                            username = '', 
                            visibility = '', 
                            website = '', ), 
                        permission = 'none', 
                        units = [repo.code, repo.issues, repo.ext_issues, repo.wiki, repo.pulls, repo.releases, repo.projects, repo.ext_wiki], 
                        units_map = {"repo.code":"read","repo.ext_issues":"none","repo.ext_wiki":"none","repo.issues":"write","repo.projects":"none","repo.pulls":"owner","repo.releases":"none","repo.wiki":"admin"}, )
                    ]
            )
        else :
            return RepoTransfer(
        )

    def testRepoTransfer(self):
        """Test RepoTransfer"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()