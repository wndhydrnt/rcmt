import datetime
from typing import Any, Union
from urllib.parse import urlparse

import gitlab
import structlog
from gitlab.v4.objects import Project as GitlabProject
from gitlab.v4.objects.merge_requests import ProjectMergeRequest as GitlabMergeRequest

from .source import PullRequest, Repository, SourceLister

log = structlog.get_logger(source="gitlab")


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

    def create_pull_request(self, branch: str, pr: PullRequest) -> None:
        log.debug(
            "Creating merge request", base=self.base_branch, head=branch, repo=str(self)
        )
        self._project.mergerequests.create(
            {
                "description": pr.body,
                "source_branch": branch,
                "target_branch": self.base_branch,
                "title": pr.title,
            }
        )

    def find_open_pull_request(self, branch: str) -> Union[Any, None]:
        log.debug("Listing merge requests", repo=str(self))
        mrs = self._project.mergerequests.list(state="opened", source_branch=branch)
        if len(mrs) == 0:
            return None

        return mrs[0]

    def has_successful_pr_build(self, identifier: GitlabMergeRequest) -> bool:
        pipelines = identifier.pipelines.list()
        if len(pipelines) == 0:
            log.debug("No pipelines", repo=str(self), id=identifier.get_id())
            return True

        for pl in pipelines:
            if pl.sha == identifier.sha and pl.status != "success":
                log.warn(
                    "Pipeline not successful",
                    pipeline_id=pl.id,
                    repo=str(self),
                    status=pl.status,
                )
                return False

        log.debug(
            "All pipeline runs successful", repo=str(self), id=identifier.get_id()
        )
        return True

    def merge_pull_request(self, identifier: GitlabMergeRequest) -> None:
        log.debug("Merging merge request", repo=str(self), id=identifier.get_id())
        identifier.merge()

    @property
    def name(self) -> str:
        return self._project.path

    def pr_created_at(self, pr: GitlabMergeRequest) -> datetime.datetime:
        corrected = pr.created_at.replace("Z", "+00:00")
        return datetime.datetime.fromisoformat(corrected)

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
        repositories: list[Repository] = []
        for p in projects:
            repositories.append(GitlabRepository(project=p, url=self.url))  # type: ignore

        return repositories
