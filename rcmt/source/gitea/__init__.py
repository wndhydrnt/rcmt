import base64
import datetime
import io
from typing import Any, Generator, TextIO, Union
from urllib.parse import urlparse

from ..source import Base, PullRequest, Repository
from .client import (
    ContentsResponse,
    CreatePullRequestOption,
    EditPullRequestOption,
    MergePullRequestOption,
)
from .client import PullRequest as GiteaPullRequest
from .client import Repository as GiteaClientRepository
from .client import RepositoryApi, UserApi
from .client.api_client import ApiClient
from .client.configuration import Configuration
from .client.exceptions import NotFoundException


class GiteaRepository(Repository):
    def __init__(
        self, repo: GiteaClientRepository, repo_api: RepositoryApi, source: str
    ):
        self.repo = repo
        self.repo_api = repo_api
        self._source = source

    @property
    def base_branch(self) -> str:
        return self.repo.default_branch

    def can_merge_pull_request(self, identifier: GiteaPullRequest) -> bool:
        return identifier.mergeable

    @property
    def clone_url(self) -> str:
        return self.repo.clone_url

    def close_pull_request(self, message: str, pr: GiteaPullRequest) -> None:
        body = EditPullRequestOption(state="closed")
        self.repo_api.repo_edit_pull_request(
            owner=self.repo.owner.login,
            repo=self.repo.name,
            index=pr.id,
            body=body,
        )

    def create_pull_request(self, branch: str, pr: PullRequest) -> None:
        body = CreatePullRequestOption(
            base=self.repo.default_branch, body=pr.body, head=branch, title=pr.title
        )
        self.repo_api.repo_create_pull_request(
            owner=self.repo.owner.login, repo=self.repo.name, body=body
        )

    def delete_branch(self, identifier: GiteaPullRequest) -> None:
        self.repo_api.repo_delete_branch(
            owner=self.repo.owner.login,
            repo=self.repo.name,
            branch=identifier.head.label,
        )

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        prs: list[GiteaPullRequest] = self.repo_api.repo_list_pull_requests(
            owner=self.repo.owner.login, repo=self.repo.name
        )
        for pr in prs:
            if pr.head.label == branch:
                return pr

        return None

    def get_file(self, path: str) -> TextIO:
        try:
            resp = self.repo_api.repo_get_contents(
                owner=self.repo.owner.login, repo=self.repo.name, filepath=path
            )
        except NotFoundException:
            raise FileNotFoundError("files does not exist")

        if resp.type != "file":
            raise FileNotFoundError("not a file")

        if resp.encoding == "base64":
            decoded = base64.standard_b64decode(resp.content)
            return io.StringIO(decoded.decode(encoding="utf-8"))
        else:
            raise RuntimeError(f"Unknown encoding '{resp.encoding}'")

    def has_file(self, path: str) -> bool:
        try:
            resp = self.repo_api.repo_get_contents(
                owner=self.repo.owner.login, repo=self.repo.name, filepath=path
            )
        except NotFoundException:
            return False

        if resp.type == "file":
            return True

        if resp.type == "dir":
            return True

        return False

    def has_successful_pr_build(self, identifier: Any) -> bool:
        # Gitea does not have its own CI system. TODO: Does it have checks?
        return True

    def is_pr_closed(self, identifier: GiteaPullRequest) -> bool:
        return identifier.state == "closed" and identifier.merged is False

    def is_pr_merged(self, identifier: GiteaPullRequest) -> bool:
        return identifier.state == "closed" and identifier.merged is True

    def is_pr_open(self, identifier: GiteaPullRequest) -> bool:
        return identifier.state == "open"

    def merge_pull_request(self, identifier: GiteaPullRequest) -> None:
        body = MergePullRequestOption(do="merge")
        self.repo_api.repo_merge_pull_request(
            owner=self.repo.owner.login,
            repo=self.repo.name,
            index=identifier.id,
            body=body,
        )

    @property
    def name(self) -> str:
        return self.repo.name

    def pr_created_at(self, pr: GiteaPullRequest) -> datetime.datetime:
        return pr.created_at

    @property
    def project(self) -> str:
        return self.repo.owner.login

    @property
    def source(self) -> str:
        return self._source

    def update_pull_request(self, pr: GiteaPullRequest, pr_data: PullRequest) -> None:
        if pr.body == pr_data.body and pr.title == pr_data.title:
            return None

        body = EditPullRequestOption(body=pr_data.body, title=pr_data.title)
        self.repo_api.repo_edit_pull_request(
            owner=self.repo.owner.login,
            repo=self.repo.name,
            index=pr.id,
            body=body,
        )


class Gitea(Base):
    def __init__(self, api_key: str, url: str):
        cfg = Configuration(host=url)
        cfg.api_key["AccessToken"] = api_key
        self.client = ApiClient(configuration=cfg)
        self.client.user_agent = "rcmt"
        self.source = urlparse(url).netloc

    def list_repositories_with_open_pull_requests(
        self,
    ) -> Generator[Repository, None, None]:
        return
        yield

    def list_repositories(self, since: datetime.datetime) -> list[Repository]:
        # TODO: Organizations of a user
        user_api = UserApi(api_client=self.client)
        repos: list[GiteaClientRepository] = user_api.user_current_list_repos()
        result: list[Repository] = []
        repo_api = RepositoryApi(api_client=self.client)
        for repo in repos:
            result.append(
                GiteaRepository(repo=repo, repo_api=repo_api, source=self.source)
            )

        return result
