import datetime
from typing import Any, Union
from urllib.parse import urlparse

import gitlab
from gitlab.v4.objects import Project as GitlabProject

from .source import PullRequest, Repository, SourceLister


class GitlabRepository(Repository):
    def __init__(self, project: GitlabProject, url: str):
        self._project = project
        self.url = url

    @property
    def base_branch(self) -> str:
        return self._project.default_branch

    @property
    def clone_url(self) -> str:
        return self._project.http_url_to_repo

    # def create_pull_request(self, branch: str, pr: PullRequest) -> None:
    #     pass

    def find_open_pull_request(self, branch: str) -> Union[Any, None]:
        prs = self._project.mergerequests.list(state="opened", source_branch=branch)
        if len(prs) == 0:
            return None

        return prs[0]

    # def has_successful_pr_build(self, identifier: Any) -> bool:
    #     pass
    #
    # def merge_pull_request(self, identifier: Any) -> None:
    #     pass

    @property
    def name(self) -> str:
        return self._project.path

    # def pr_created_at(self, pr: Any) -> datetime.datetime:
    #     pass

    @property
    def project(self) -> str:
        return self._project.namespace["path"]

    @property
    def source(self) -> str:
        return self.url


class Gitlab(SourceLister):
    def __init__(self, url: str, private_token: str):
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.url = urlparse(url).netloc

    def list_repositories(self) -> list[Repository]:
        projects = self.client.projects.list(
            all=True, archived=False, min_access_level=30
        )
        repositories: list[GitlabRepository] = []
        for p in projects:
            repositories.append(GitlabRepository(project=p, url=self.url))

        return repositories
