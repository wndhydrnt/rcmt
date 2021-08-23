import datetime
from typing import Any, Union


class PullRequest:
    def __init__(
        self,
        title_prefix: str,
        title_body: str,
        title_suffix: str,
        custom_body="",
        custom_title="",
    ):
        self.custom_body = custom_body
        self.custom_title = custom_title
        self.title_prefix = title_prefix
        self.title_body = title_body
        self.title_suffix = title_suffix

        self.changed_packages: list[str] = []

    def __eq__(self, other: object) -> bool:
        """
        Aids with checking equality during unit tests.

        :param other: Other PullRequest
        :return: bool
        """
        if self.custom_body != getattr(other, "custom_body"):
            return False

        if self.custom_title != getattr(other, "custom_title"):
            return False

        if self.title_prefix != getattr(other, "title_prefix"):
            return False

        if self.title_body != getattr(other, "title_body"):
            return False

        if self.title_suffix != getattr(other, "title_suffix"):
            return False

        return self.changed_packages == getattr(other, "changed_packages")

    def add_package(self, name: str):
        self.changed_packages.append(name)

    @property
    def body(self) -> str:
        if self.custom_body != "":
            return self.custom_body

        return f"""This update contains changes from the following packages:

{self.render_package_list()}

---

_This pull request has been created by [rcmt](https://rcmt.readthedocs.io/)._
"""

    def render_package_list(self) -> str:
        items = [f"- {n}" for n in self.changed_packages]
        return "\n".join(items)

    @property
    def title(self) -> str:
        if self.custom_title != "":
            return self.custom_title

        return f"{self.title_prefix} {self.title_body} {self.title_suffix}"


class Repository:
    def __str__(self):
        return f"{self.source}/{self.project}/{self.name}"

    @property
    def base_branch(self) -> str:
        """
        Name of the base branch of this repository.

        :return: str
        """
        raise NotImplementedError("class does not implement Repository.base_branch()")

    @property
    def clone_url(self) -> str:
        """
        Url to clone this repository.

        :return: str
        """
        raise NotImplementedError("class does not implement Repository.clone_url()")

    def create_pull_request(self, branch: str, pr: PullRequest) -> None:
        """
        Creates a pull request for the given branch.

        :param branch: Name of the branch.
        :param pr: The pull request.
        :return: None
        """
        raise NotImplementedError(
            "class does not implement Repository.create_pull_request()"
        )

    def find_open_pull_request(self, branch: str) -> Union[Any, None]:
        """
        Finds and returns the pull request opened by rcmt.

        :param branch: Name of the branch from which a pull request has been created.
        :return: Implementation of this method should return None if no pull request is open. Any other value will be
                 passed to merge_pull_request() so it can identify which PR to merge.
        """
        raise NotImplementedError(
            "class does not implement Repository.has_open_pull_request()"
        )

    def has_successful_pr_build(self, identifier: Any) -> bool:
        """
        Checks if a pull request has passed all checks. rcmt will call merge_pull_request if this function returns
        True.

        :param identifier: Data to identify the pull request as returned by find_open_pull_request.
        :return: bool
        """
        raise NotImplementedError(
            "class does not implement Repository.has_successful_build()"
        )

    def merge_pull_request(self, identifier: Any) -> None:
        """
        Merges a pull request.

        :param identifier: Data to identify the pull request as returned by find_open_pull_request.
        :return: None
        """
        raise NotImplementedError(
            "class does not implement Repository.merge_pull_request()"
        )

    @property
    def name(self) -> str:
        """
        Name of the repository.

        :return: str
        """
        raise NotImplementedError("class does not implement Repository.name()")

    def pr_created_at(self, pr: Any) -> datetime.datetime:
        """
        Returns the date and time at which the pull request was created.

        :param pr: The pull request identifier as returned by find_open_pull_request().
        :return: datetime.datetime
        """
        raise NotImplementedError("class does not implement Repository.pr_created_at()")

    @property
    def project(self) -> str:
        """
        Name of the project the repository belongs to.

        :return: str
        """

        raise NotImplementedError("class does not implement Repository.project()")

    @property
    def source(self) -> str:
        """
        Name of the source that hosts the repository.

        :return: str
        """
        raise NotImplementedError("class does not implement Repository.source()")


class Source:
    pass


class SourceLister:
    def list_repositories(self) -> list[Repository]:
        raise NotImplementedError(
            "class does not implement SourceLister.list_repositories()"
        )
