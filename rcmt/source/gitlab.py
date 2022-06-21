import datetime
import fnmatch
import io
import os.path
from typing import Any, TextIO, Union
from urllib.parse import urlparse

import gitlab
import structlog
from gitlab import GitlabGetError
from gitlab.base import RESTObjectList
from gitlab.v4.objects import Project as GitlabProject
from gitlab.v4.objects.merge_requests import ProjectMergeRequest as GitlabMergeRequest

from ..log import SECRET_MASKER
from .source import Base, PullRequest, Repository, add_credentials_to_url

log: structlog.stdlib.BoundLogger = structlog.get_logger(source="gitlab")


class GitlabRepository(Repository):
    def __init__(self, project: GitlabProject, token: str, url: str):
        self._project = project
        self.token = token
        self.url = url

    @property
    def base_branch(self) -> str:
        return self._project.default_branch

    @property
    def clone_url(self) -> str:
        # Value of username does not matter to GitLab.
        return add_credentials_to_url(
            url=self._project.http_url_to_repo, password=self.token, username="rcmt"
        )

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

    def get_file(self, path: str) -> TextIO:
        try:
            content = self._project.files.get(
                file_path=path, ref=self.base_branch
            ).decode()
            if content is None:
                log.warning("Decoded content is None", repo=str(self), file=path)
                raise FileNotFoundError("decoded content is None")

            return io.StringIO(content.decode("utf-8"))
        except GitlabGetError:
            raise FileNotFoundError("file does not exist in repository")

    def has_file(self, path: str) -> bool:
        directory = os.path.dirname(path)
        file = os.path.basename(path)
        tree = self._project.repository_tree(path=directory)
        for entry in tree:
            if entry["type"] != "blob":
                continue

            if fnmatch.fnmatch(entry["path"], file):
                return True

        return False

    def has_successful_pr_build(self, identifier: GitlabMergeRequest) -> bool:
        failed = False
        for commit_status in self._project.commits.get(identifier.sha).statuses.list():
            if commit_status.allow_failure is True:
                continue

            if commit_status.status != "success":
                log.debug(
                    "MR check failed",
                    repo=str(self),
                    id=identifier.get_id(),
                    name=commit_status.name,
                    status=commit_status.status,
                )
                failed = True

        if failed is False:
            log.debug(
                "All MR checks successful", repo=str(self), id=identifier.get_id()
            )
            return True

        return False

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
        return self._project.namespace["full_path"]

    @property
    def source(self) -> str:
        return self.url


class Gitlab(Base):
    def __init__(self, url: str, private_token: str):
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.url = urlparse(url).netloc

        SECRET_MASKER.add_secret(private_token)

    def list_repositories(self) -> list[Repository]:
        log.debug("start fetching repositories")
        projects = self.client.projects.list(
            all=True, archived=False, min_access_level=30
        )
        repositories: list[Repository] = []
        for p in projects:
            repositories.append(GitlabRepository(project=p, token=self.client.private_token, url=self.url))  # type: ignore

        log.debug("finished fetching repositories")
        return repositories
