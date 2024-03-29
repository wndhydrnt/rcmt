# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import fnmatch
import io
import os.path
from typing import Any, Generator, Iterator, Optional, TextIO, Union
from urllib.parse import urlparse

import gitlab
from gitlab import GitlabGetError
from gitlab.base import RESTObjectList
from gitlab.v4.objects import CurrentUser
from gitlab.v4.objects import Project as GitlabProject
from gitlab.v4.objects.merge_requests import ProjectMergeRequest as GitlabMergeRequest

import rcmt.log

from .source import (
    Base,
    PullRequest,
    PullRequestComment,
    Repository,
    add_credentials_to_url,
)

log = rcmt.log.get_logger(__name__)


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

    def create_pr_comment(self, body: str, pr: GitlabMergeRequest) -> None:
        pr.notes.create({"body": body})

    def create_pull_request(self, branch: str, pr: PullRequest) -> None:
        log.debug(
            "Creating merge request branch=%s base_branch=%s", branch, self.base_branch
        )
        payload: dict[str, Any] = {
            "description": pr.body,
            "source_branch": branch,
            "target_branch": self.base_branch,
            "title": pr.title,
        }
        if pr.labels is not None and len(pr.labels) > 0:
            payload["labels"] = pr.labels

        self._project.mergerequests.create(payload)

    def delete_branch(self, identifier: GitlabMergeRequest) -> None:
        if identifier.should_remove_source_branch is not True:
            self._project.branches.get(id=identifier.source_branch, lazy=True).delete()

    def delete_pr_comment(
        self, comment: PullRequestComment, pr: GitlabMergeRequest
    ) -> None:
        pr.notes.delete(comment.id)

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        log.debug("Listing merge requests")
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
                log.warning("Decoded content is None file=%s", path)
                raise FileNotFoundError("decoded content is None")

            return io.StringIO(content.decode("utf-8"))
        except GitlabGetError:
            raise FileNotFoundError("file does not exist in repository")

    def get_pr_body(self, mr: GitlabMergeRequest) -> str:
        return mr.description

    def has_file(self, path: str) -> bool:
        directory = os.path.dirname(path)
        try:
            tree = self._project.repository_tree(path=directory, iterator=True)
            for entry in tree:
                if entry["type"] != "blob":
                    continue

                if fnmatch.fnmatch(entry["path"], path):
                    return True
        except gitlab.GitlabGetError as e:
            if e.response_code == 404:
                log.warning("Tree not found - empty repository?")
                return False
            else:
                raise e

        return False

    def has_successful_pr_build(self, identifier: GitlabMergeRequest) -> bool:
        if identifier.approvals.get().approved is False:
            log.debug("Approvals missing mr_id=%s", identifier.get_id())
            return False

        failed = False
        for commit_status in self._project.commits.get(
            id=identifier.sha, lazy=True
        ).statuses.list(iterator=True):
            if commit_status.allow_failure is True:
                continue

            if commit_status.status != "success":
                log.debug(
                    "Merge request check failed mr_id=%s name=%s status=%s",
                    identifier.get_id(),
                    commit_status.name,
                    commit_status.status,
                )
                failed = True

        if failed is False:
            log.debug("All MR checks successful mr_id=%s", identifier.get_id())
            return True

        return False

    def is_pr_closed(self, mr: GitlabMergeRequest) -> bool:
        return mr.state == "closed" or mr.state == "locked"

    def is_pr_merged(self, mr: GitlabMergeRequest) -> bool:
        return mr.state == "merged"

    def is_pr_open(self, mr: GitlabMergeRequest) -> bool:
        return mr.state == "opened"

    def list_pr_comments(self, mr: GitlabMergeRequest) -> Iterator[PullRequestComment]:
        if mr is None:
            return []

        for note in mr.notes.list(iterator=True):
            yield PullRequestComment(body=note.body, id=note.id)

    def merge_pull_request(self, identifier: GitlabMergeRequest):
        log.debug("Merging merge request mr_id=%s", identifier.get_id())
        identifier.merge()

    @property
    def name(self) -> str:
        return self._project.path

    def pr_created_at(self, pr: GitlabMergeRequest) -> datetime.datetime:
        corrected: str = pr.created_at.replace("Z", "")
        return datetime.datetime.fromisoformat(corrected).replace(
            tzinfo=datetime.timezone.utc
        )

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
            log.debug("Updating merge request data mr_id=%s", pr.get_id())
            pr.save()


class Gitlab(Base):
    def __init__(self, url: str, private_token: str):
        self.client = gitlab.Gitlab(url, private_token=private_token)
        self.url = urlparse(url).netloc

    def create_from_name(self, name: str) -> Optional[Repository]:
        if name.startswith(self.url) is False:
            return None

        name_without_host = name.replace(f"{self.url}/", "")
        try:
            p = self.client.projects.get(id=name_without_host)
        except gitlab.GitlabGetError as e:
            log.debug(
                "Unable to get project project_name=%s, status_code=%d",
                name,
                e.response_code,
            )
            return None

        token = self.client.private_token or ""
        return GitlabRepository(project=p, token=token, url=self.url)

    def list_repositories_with_open_pull_requests(
        self,
    ) -> Generator[Repository, None, None]:
        if self.client.user is None:
            self.client.auth()

        user: Optional[CurrentUser] = self.client.user
        if user is None:
            log.error("Unable to authenticate user while listing open pull requests")
            return

        merge_requests = self.client.mergerequests.list(
            author_id=user.attributes["id"], iterator=True, state="opened"
        )
        seen_project_ids: list[int] = []
        for mr in merge_requests:
            if mr.project_id in seen_project_ids:
                continue

            seen_project_ids.append(mr.project_id)
            project = self.client.projects.get(id=mr.project_id)
            if project.archived is True:
                log.debug(
                    "Ignore project because it has been archived project=%s",
                    project.path_with_namespace,
                )
                continue

            repository = GitlabRepository(
                project=project, token=self.client.private_token, url=self.url  # type: ignore
            )
            yield repository

    def list_repositories(self, since: datetime.datetime) -> Iterator[Repository]:
        log.debug("Start fetching repositories")
        projects = self.client.projects.list(
            archived=False,
            last_activity_after=since,
            iterator=True,
            min_access_level=30,
        )
        for p in projects:
            yield GitlabRepository(
                project=p, token=self.client.private_token, url=self.url  # type: ignore
            )

        log.debug("Finished fetching repositories")
