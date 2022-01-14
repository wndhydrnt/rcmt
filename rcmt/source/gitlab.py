import datetime
from typing import Any, Union
from urllib.parse import urlparse

import gitlab
import structlog
from gitlab.base import RESTObjectList
from gitlab.v4.objects import Project as GitlabProject
from gitlab.v4.objects.merge_requests import ProjectMergeRequest as GitlabMergeRequest

from .source import Base, PullRequest, Repository

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

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        log.debug("Listing merge requests", repo=str(self))
        mrs = self._project.mergerequests.list(state="all", source_branch=branch)
        if len(mrs) == 0:
            return None

        if isinstance(mrs, list):
            return mrs[0]

        if isinstance(mrs, RESTObjectList):
            return mrs.next()

        raise RuntimeError(
            f"GitLab API returned an unexpected object {mrs.__class__.__name__}"
        )

    def has_file(self, path: str) -> bool:
        try:
            self._project.files.get(file_path=path, ref=self.base_branch)
        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                return False
            else:
                raise e

        return True

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

    def is_pr_closed(self, mr: GitlabMergeRequest) -> bool:
        return mr.state == "closed" or mr.state == "locked"

    def is_pr_merged(self, mr: GitlabMergeRequest) -> bool:
        return mr.state == "merged"

    def is_pr_open(self, mr: GitlabMergeRequest) -> bool:
        return mr.state == "opened"

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


class Gitlab(Base):
    def __init__(self, url: str, private_token: str):
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.url = urlparse(url).netloc

    def list_repositories(self) -> list[Repository]:
        log.debug("start fetching repositories")
        projects = self.client.projects.list(
            all=True, archived=False, min_access_level=30
        )
        repositories: list[Repository] = []
        for p in projects:
            repositories.append(GitlabRepository(project=p, url=self.url))  # type: ignore

        log.debug("finished fetching repositories")
        return repositories
