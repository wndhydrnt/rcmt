import datetime
import fnmatch
import io
import os.path
from typing import Any, Generator, Optional, TextIO, Union
from urllib.parse import urlparse

import gitlab
import structlog
from gitlab import GitlabGetError
from gitlab.base import RESTObjectList
from gitlab.v4.objects import CurrentUser
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

    def can_merge_pull_request(self, identifier: GitlabMergeRequest) -> bool:
        return True

    @property
    def clone_url(self) -> str:
        # Value of username does not matter to GitLab.
        return add_credentials_to_url(
            url=self._project.http_url_to_repo, password=self.token, username="rcmt"
        )

    def close_pull_request(self, message: str, pr: GitlabMergeRequest) -> None:
        pr.notes.create({"body": message})
        pr.state_event = "close"
        pr.save()

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

    def delete_branch(self, identifier: GitlabMergeRequest) -> None:
        if identifier.should_remove_source_branch is not True:
            self._project.branches.get(id=identifier.source_branch, lazy=True).delete()

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        log.debug("Listing merge requests", repo=str(self))
        mrs = self._project.mergerequests.list(
            all=False, state="all", source_branch=branch
        )
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
        try:
            tree = self._project.repository_tree(path=directory, iterator=True)
            for entry in tree:
                if entry["type"] != "blob":
                    continue

                if fnmatch.fnmatch(entry["path"], file):
                    return True
        except gitlab.GitlabGetError as e:
            if e.response_code == 404:
                log.warning("Tree not found - empty repository?", repo=str(self))
                return False
            else:
                raise e

        return False

    def has_successful_pr_build(self, identifier: GitlabMergeRequest) -> bool:
        if identifier.approvals.get().approved is False:
            log.debug("Approvals missing", repo=str(self), id=identifier.get_id())
            return False

        failed = False
        for commit_status in self._project.commits.get(
            id=identifier.sha, lazy=True
        ).statuses.list(iterator=True):
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

    def merge_pull_request(self, identifier: GitlabMergeRequest):
        log.debug("Merging merge request", repo=str(self), id=identifier.get_id())
        identifier.merge()

    @property
    def name(self) -> str:
        return self._project.path

    def pr_created_at(self, pr: GitlabMergeRequest) -> datetime.datetime:
        corrected: str = pr.created_at.replace("Z", "")
        return datetime.datetime.fromisoformat(corrected)

    @property
    def project(self) -> str:
        return self._project.namespace["full_path"]

    @property
    def source(self) -> str:
        return self.url

    def update_pull_request(self, pr: GitlabMergeRequest, pr_data: PullRequest) -> None:
        needs_update = False
        if pr.title != pr_data.title:
            pr.title = pr_data.title
            needs_update = True

        if pr.description != pr_data.body:
            pr.description = pr_data.body
            needs_update = True

        if needs_update is True:
            log.debug("Updating MR data", id=pr.get_id(), repo=str(self))
            pr.save()


class Gitlab(Base):
    def __init__(self, url: str, private_token: str):
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.url = urlparse(url).netloc

        SECRET_MASKER.add_secret(private_token)

    def list_repositories_with_open_pull_requests(
        self,
    ) -> Generator[Repository, None, None]:
        if self.client.user is None:
            self.client.auth()

        user: Optional[CurrentUser] = self.client.user
        if user is None:
            log.error("unable to authenticate user while listing open pull requests")
            return

        merge_requests = self.client.mergerequests.list(
            author_id=user.attributes["id"], state="opened"
        )
        seen_project_ids: list[int] = []
        for mr in merge_requests:
            if mr.project_id in seen_project_ids:
                continue

            seen_project_ids.append(mr.project_id)
            project = self.client.projects.get(id=mr.project_id)
            repository = GitlabRepository(
                project=project, token=self.client.private_token, url=self.url  # type: ignore
            )
            yield repository

    def list_repositories(self, since: datetime.datetime) -> list[Repository]:
        log.debug("start fetching repositories")
        projects = self.client.projects.list(
            all=True, archived=False, min_access_level=30, last_activity_after=since
        )
        repositories: list[Repository] = []
        for p in projects:
            repositories.append(GitlabRepository(project=p, token=self.client.private_token, url=self.url))  # type: ignore

        log.debug("finished fetching repositories")
        return repositories
