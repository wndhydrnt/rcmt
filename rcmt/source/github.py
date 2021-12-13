import datetime
from typing import Any, Union

import github
import github.PullRequest
import github.Repository
import structlog

from .source import Base, PullRequest, Repository

log = structlog.get_logger(source="github")


class GithubRepository(Repository):
    def __init__(self, repo: github.Repository.Repository):
        self.repo = repo
        self._clone_url = repo.clone_url
        self._name = repo.name
        self._project = repo.owner.login

    @property
    def base_branch(self) -> str:
        return self.repo.default_branch

    @property
    def clone_url(self):
        return self.repo.clone_url

    def create_pull_request(self, branch: str, pr: PullRequest):
        log.debug(
            "Creating pull request", base=self.base_branch, head=branch, repo=str(self)
        )
        self.repo.create_pull(
            title=pr.title,
            body=pr.body,
            base=self.base_branch,
            head=branch,
            maintainer_can_modify=True,
        )

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        log.debug("Listing pull requests", repo=str(self))
        for pr in self.repo.get_pulls(state="all"):
            if pr.head.ref == branch:
                return pr

        return None

    def has_file(self, path: str) -> bool:
        try:
            self.repo.get_contents(path=path, ref=self.base_branch)
        except github.UnknownObjectException as e:
            if e.status == 404:
                return False
            else:
                raise e

        return True

    def has_successful_pr_build(self, pr: github.PullRequest.PullRequest) -> bool:
        log.debug("Checking PR builds", repo=str(self))
        for cr in self.repo.get_commit(pr.head.sha).get_check_runs():
            if cr.conclusion != "success":
                log.debug(
                    "GitHub check not successful",
                    repo=str(self),
                    check_name=cr.name,
                    check_conclusion=cr.conclusion,
                )
                return False

        return True

    def is_pr_closed(self, pr: github.PullRequest.PullRequest) -> bool:
        return pr.state == "closed" and pr.merged is False

    def is_pr_merged(self, pr: github.PullRequest.PullRequest) -> bool:
        return pr.state == "closed" and pr.merged is True

    def is_pr_open(self, pr: github.PullRequest.PullRequest) -> bool:
        return pr.state == "open"

    def merge_pull_request(self, pr: github.PullRequest.PullRequest):
        if pr.mergeable:
            log.debug("Merging pull request", repo=str(self))
            pr.merge(commit_title="Auto-merge by rcmt")
        else:
            log.warn(
                "GitHub indicates that the PR is not mergeable",
                pr_id=pr.id,
                repo=str(self),
            )

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


class Github(Base):
    def __init__(self, access_token: str, base_url: str):
        self.client = github.Github(login_or_token=access_token, base_url=base_url)

    def list_repositories(self) -> list[Repository]:
        log.debug("start fetching repositories")
        repos: list[Repository] = []
        for gh_repo in self.client.get_user().get_repos():
            repos.append(GithubRepository(gh_repo))

        log.debug("finished fetching repositories")
        return repos
