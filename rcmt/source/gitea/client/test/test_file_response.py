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
from rcmt.source.gitea.client.models.file_response import FileResponse  # noqa: E501
from rcmt.source.gitea.client.rest import ApiException

class TestFileResponse(unittest.TestCase):
    """FileResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test FileResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = rcmt.source.gitea.client.models.file_response.FileResponse()  # noqa: E501
        if include_optional :
            return FileResponse(
                commit = rcmt.source.gitea.client.models.file_commit_response_contains_information_generated_from_a_git_commit_for_a_repo's_file/.FileCommitResponse contains information generated from a Git commit for a repo's file.(
                    author = rcmt.source.gitea.client.models.commit_user_contains_information_of_a_user_in_the_context_of_a_commit/.CommitUser contains information of a user in the context of a commit.(
                        date = '', 
                        email = '', 
                        name = '', ), 
                    committer = rcmt.source.gitea.client.models.commit_user_contains_information_of_a_user_in_the_context_of_a_commit/.CommitUser contains information of a user in the context of a commit.(
                        date = '', 
                        email = '', 
                        name = '', ), 
                    created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    html_url = '', 
                    message = '', 
                    parents = [
                        rcmt.source.gitea.client.models.commit_meta_contains_meta_information_of_a_commit_in_terms_of_api/.CommitMeta contains meta information of a commit in terms of API.(
                            created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            sha = '', 
                            url = '', )
                        ], 
                    sha = '', 
                    tree = rcmt.source.gitea.client.models.commit_meta_contains_meta_information_of_a_commit_in_terms_of_api/.CommitMeta contains meta information of a commit in terms of API.(
                        created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        sha = '', 
                        url = '', ), 
                    url = '', ), 
                content = rcmt.source.gitea.client.models.contents_response.ContentsResponse(
                    _links = rcmt.source.gitea.client.models.file_links_response.FileLinksResponse(
                        git = '', 
                        html = '', 
                        self = '', ), 
                    content = '', 
                    download_url = '', 
                    encoding = '', 
                    git_url = '', 
                    html_url = '', 
                    last_commit_sha = '', 
                    name = '', 
                    path = '', 
                    sha = '', 
                    size = 56, 
                    submodule_git_url = '', 
                    target = '', 
                    type = '', 
                    url = '', ), 
                verification = rcmt.source.gitea.client.models.payload_commit_verification.PayloadCommitVerification(
                    payload = '', 
                    reason = '', 
                    signature = '', 
                    signer = rcmt.source.gitea.client.models.payload_user.PayloadUser(
                        email = '', 
                        name = '', 
                        username = '', ), 
                    verified = True, )
            )
        else :
            return FileResponse(
        )

    def testFileResponse(self):
        """Test FileResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
