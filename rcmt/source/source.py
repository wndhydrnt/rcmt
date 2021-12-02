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
    """
    Repository provides all methods needed to interact with a single repository of a
    Source.
    """

    def __str__(self):
        return f"{self.source}/{self.project}/{self.name}"

    @property
    def base_branch(self) -> str:
        """
        :return: Name of the base branch of this repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.base_branch()")

    @property
    def clone_url(self) -> str:
        """
        :return: Url to clone this repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.clone_url()")

    def create_pull_request(self, branch: str, pr: PullRequest) -> None:
        """
        Creates a pull request for the given branch.

        :param branch: Name of the branch.
        :param pr: The pull request.
        :rtype: None
        """
        raise NotImplementedError(
            "class does not implement Repository.create_pull_request()"
        )

    def find_pull_request(self, branch: str) -> Union[Any, None]:
        """
        Finds and returns the pull request opened by rcmt.

        :param branch: Name of the branch from which a pull request has been created.
        :return: Implementation of this method should return None if no pull request is open. Any other value will be
                 passed to merge_pull_request() so it can identify which PR to merge.
        :rtype: Any, None
        """
        raise NotImplementedError(
            "class does not implement Repository.has_open_pull_request()"
        )

    def has_file(self, path: str) -> bool:
        """
        Checks if a file exists in a repository.

        rcmt calls this function when matching repositories. This is more efficient than
        checking out the whole repository to check if a file exists.

        :param path: Path to a file or directory in the repository.
        :return: Indicates if the files exists.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.has_file()")

    def has_successful_pr_build(self, identifier: Any) -> bool:
        """
        Checks if a pull request has passed all checks. rcmt will call merge_pull_request if this function returns
        True.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates if the build is successful.
        :rtype: bool
        """
        raise NotImplementedError(
            "class does not implement Repository.has_successful_build()"
        )

    def is_pr_closed(self, identifier: Any) -> bool:
        """
        Checks if a pull request has been closed by the user.
        A pull request is closed if a user manually closes it without merging it.
        If a user has closed a pull request without merging it, rcmt will not create a
        new one.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates that a pull request has been closed by the user.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.is_pr_closed()")

    def is_pr_merged(self, identifier: Any) -> bool:
        """
        Checks if a pull request has been merged.
        rcmt uses this information to determine if it can create new pull requests.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates that a pull request has been merged.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.is_pr_merged()")

    def is_pr_open(self, identifier: Any) -> bool:
        """
        Checks if a pull request is open.
        rcmt will attempt to merge the pull request if this method returns true and
        there are no new changes from packages.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :return: Indicates that a pull request is open.
        :rtype: bool
        """
        raise NotImplementedError("class does not implement Repository.is_pr_open()")

    def merge_pull_request(self, identifier: Any) -> None:
        """
        Merges a pull request.

        :param identifier: Data to identify the pull request as returned by find_pull_request.
        :rtype: None
        """
        raise NotImplementedError(
            "class does not implement Repository.merge_pull_request()"
        )

    @property
    def name(self) -> str:
        """
        :return: Name of the repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.name()")

    def pr_created_at(self, pr: Any) -> datetime.datetime:
        """
        Returns the date and time at which the pull request was created.

        :param pr: The pull request identifier as returned by find_pull_request().
        :return: Date and time at which the pull request was created.
        :rtype: datetime.datetime
        """
        raise NotImplementedError("class does not implement Repository.pr_created_at()")

    @property
    def project(self) -> str:
        """
        :return: Name of the project the repository belongs to.
        :rtype: str
        """

        raise NotImplementedError("class does not implement Repository.project()")

    @property
    def source(self) -> str:
        """
        :return: Name of the source that hosts the repository.
        :rtype: str
        """
        raise NotImplementedError("class does not implement Repository.source()")


class Base:
    """
    Base defines the methods every Source needs to implement.

    """

    def list_repositories(self) -> list[Repository]:
        """
        :return: List of all known repositories.
        :rtype: list[rcmt.source.Repository]
        """
        raise NotImplementedError(
            "class does not implement SourceLister.list_repositories()"
        )
