# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import fnmatch
import io
from typing import Any, Generator, Iterator, Optional, TextIO, Union

import github
import github.Auth
import github.PullRequest
import github.Repository

import rcmt.log

from .source import (
    Base,
    PullRequest,
    PullRequestComment,
    Repository,
    add_credentials_to_url,
)

log = rcmt.log.get_logger(__name__)


class GithubRepository(Repository):
    def __init__(self, access_token: str, repo: github.Repository.Repository):
        self.access_token = access_token
        self.repo = repo
        self._name = repo.name
        self._project = repo.owner.login

    @property
    def base_branch(self) -> str:
        return self.repo.default_branch

    def can_merge_pull_request(
        self, identifier: github.PullRequest.PullRequest
    ) -> bool:
        if identifier.mergeable is None:
            return True

        if identifier.mergeable is False:
            log.warning(
                "GitHub indicates that the PR is not mergeable pr_id=%s", identifier.id
            )

        return identifier.mergeable

    @property
    def clone_url(self):
        return add_credentials_to_url(
            url=self.repo.clone_url, password=self.access_token
        )

    def close_pull_request(
        self, message: str, pr: github.PullRequest.PullRequest
    ) -> None:
        pr.create_issue_comment(body=message)
        pr.edit(state="closed")

    def create_pr_comment(self, body: str, pr: github.PullRequest.PullRequest) -> None:
        pr.create_issue_comment(body=body)

    def create_pull_request(self, branch: str, pr: PullRequest):
        log.debug(
            "Creating pull request branch=%s base_branch=%s", branch, self.base_branch
        )
        gh_pr = self.repo.create_pull(
            title=pr.title,
            body=pr.body,
            base=self.base_branch,
            head=branch,
            maintainer_can_modify=True,
        )

        if pr.labels is not None and len(pr.labels) > 0:
            gh_pr.set_labels(*pr.labels)

    def delete_branch(self, identifier: github.PullRequest.PullRequest) -> None:
        if self.repo.delete_branch_on_merge is False:
            self.repo.get_git_ref(ref=f"heads/{identifier.head.ref}").delete()

    def delete_pr_comment(
        self, comment: PullRequestComment, pr: github.PullRequest.PullRequest
    ) -> None:
        pr.get_issue_comment(comment.id).delete()

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        log.debug("Listing pull requests")
        for pr in self.repo.get_pulls(state="all"):
            if pr.head.ref == branch:
                return pr

        return None

    def get_file(self, path: str) -> TextIO:
        try:
            file = self.repo.get_contents(path=path, ref=self.base_branch)
        except github.UnknownObjectException:
            raise FileNotFoundError("file does not exist in repository")

        if isinstance(file, list):
            if len(file) != 1:
                raise FileNotFoundError("github returned more than one file")

            file = file[0]

        return io.StringIO(file.decoded_content.decode("utf-8"))

    def get_pr_body(self, pr: github.PullRequest.PullRequest) -> str:
        return pr.body

    def has_file(self, path: str) -> bool:
        try:
            tree = self.repo.get_git_tree(self.base_branch, True)
            for entry in tree.tree:
                if fnmatch.fnmatch(entry.path, path):
                    return True
        except github.GithubException as e:
            if e.status == 409:
                log.warning("Tree not found - empty repository?")
                return False
            else:
                raise e

        return False

    def has_successful_pr_build(self, pr: github.PullRequest.PullRequest) -> bool:
        log.debug("Checking PR builds")
        for cr in self.repo.get_commit(pr.head.sha).get_check_runs():
            if cr.conclusion != "success":
                log.debug(
                    "GitHub check not successful check=%s conclusion=%s",
                    cr.name,
                    cr.conclusion,
                )
                return False

        return True

    def is_pr_closed(self, pr: github.PullRequest.PullRequest) -> bool:
        return pr.state == "closed" and pr.merged is False

    def is_pr_merged(self, pr: github.PullRequest.PullRequest) -> bool:
        return pr.state == "closed" and pr.merged is True

    def is_pr_open(self, pr: github.PullRequest.PullRequest) -> bool:
        return pr.state == "open"

    def list_pr_comments(
        self, pr: github.PullRequest.PullRequest
    ) -> Iterator[PullRequestComment]:
        if pr is None:
            return []

        for issue in pr.get_issue_comments():
            yield PullRequestComment(body=issue.body, id=issue.id)

    def merge_pull_request(self, pr: github.PullRequest.PullRequest) -> None:
        log.debug("Merging pull request pr_id=%s", pr.id)
        pr.merge(commit_title="Auto-merge by rcmt")

    @property
    def name(self) -> str:
        return self.repo.name

    def pr_created_at(self, pr: github.PullRequest.PullRequest) -> datetime.datetime:
        return pr.created_at

    @property
    def project(self) -> str:
        return self.repo.owner.login

    @property
    def source(self) -> str:
        return "github.com"

    def update_pull_request(
        self, pr: github.PullRequest.PullRequest, pr_data: PullRequest
    ) -> None:
        needs_update = False
        if pr.title != pr_data.title:
            needs_update = True

        if pr.body != pr_data.body:
            needs_update = True

        if needs_update is True:
            log.debug("Updating PR data pr_id=%s", pr.id)
            pr.edit(title=pr_data.title, body=pr_data.body)


class Github(Base):
    def __init__(self, access_token: str, base_url: str):
        self.access_token = access_token
        self.client = github.Github(
            auth=github.Auth.Token(token=access_token),
            base_url=base_url,
        )

    def create_from_name(self, name: str) -> Optional[Repository]:
        repo_name = "/".join(name.split("/")[1:])
        try:
            gh_repo = self.client.get_repo(full_name_or_id=repo_name, lazy=False)
        except github.UnknownObjectException:
            return None

        return GithubRepository(access_token=self.access_token, repo=gh_repo)

    def list_repositories_with_open_pull_requests(
        self,
    ) -> Generator[Repository, None, None]:
        user = self.client.get_user()
        for issue in self.client.search_issues(
            f"is:open is:pr author:{user.login} archived:false"
        ):
            yield GithubRepository(self.access_token, issue.repository)

    def list_repositories(self, since: datetime.datetime) -> Iterator[Repository]:
        log.debug("Start fetching repositories")
        for gh_repo in self.client.get_user().get_repos(
            direction="desc", sort="updated"
        ):
            if gh_repo.updated_at > since:
                yield GithubRepository(self.access_token, gh_repo)
            else:
                break

        log.debug("Finished fetching repositories")
